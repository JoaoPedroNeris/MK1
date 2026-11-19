"""MK I v0.2c - configuracao e teste de bancada dos 6 STS3215 (12 V) pela Waveshare Bus Servo Adapter (A).

AINDA NAO TESTADO COM HARDWARE (escrito em 19/11/2026, antes dos servos chegarem).
Rode cada passo com o braco DESMONTADO ou com o servo solto na mesa ate conferir que se comporta.

Instalar:   pip install feetech-servo-sdk pyserial
Jumper da Waveshare na posicao B (USB). Descobrir a porta no Gerenciador de Dispositivos (ex.: COM5).

Passos (na ordem):
  python configurar_servos.py --porta COM5 procurar                 # lista os IDs que respondem
  python configurar_servos.py --porta COM5 id --de 1 --para 4       # UM servo por vez no barramento!
  python configurar_servos.py --porta COM5 ler                       # posicao, carga, tensao, temperatura de todos
  python configurar_servos.py --porta COM5 protecoes                 # grava limites de seguranca na EEPROM (todos)
  python configurar_servos.py --porta COM5 centro --ids 2 3          # liga torque e leva a 2048 (montar o garfo do ombro assim)
  python configurar_servos.py --porta COM5 soltar                    # desliga o torque de todos
  python configurar_servos.py --porta COM5 ombro                     # monitora a carga dos 2 servos do ombro (Ctrl+C sai)
  python configurar_servos.py --porta COM5 offset --id 3 --passos -12  # ajuste fino do ombro B (grava na EEPROM)

Mapa de IDs (decisao 18/11): 1 giro, 2 ombro A, 3 ombro B (espelhado), 4 cotovelo, 5 punho, 6 garra.
"""
import argparse
import sys
import time

try:
    from scservo_sdk import PortHandler, PacketHandler, GroupSyncWrite, COMM_SUCCESS
except ImportError:
    sys.exit("Falta o SDK: pip install feetech-servo-sdk pyserial")

BAUD = 1_000_000          # padrao de fabrica do STS3215
NOMES = {1: "giro", 2: "ombro A", 3: "ombro B", 4: "cotovelo", 5: "punho", 6: "garra"}
ESPELHADO = {3}           # ombro B gira ao contrario do ombro A: alvo_B = 4095 - alvo_A (+ offset)

# Tabela de memoria do STS3215 (enderecos usados aqui)
ID, BAUD_REG = 5, 6
MIN_POS, MAX_POS = 9, 11
MAX_TEMP, MAX_VOLT, MIN_VOLT = 13, 14, 15
MAX_TORQUE = 16
PROT_CURRENT = 28
OFFSET = 31               # 2 bytes, bit 11 = sinal
PROT_TORQUE, PROT_TIME, OVERLOAD_TORQUE = 34, 35, 36
TORQUE_ENABLE, ACCEL, GOAL_POS = 40, 41, 42
GOAL_SPEED = 46
TORQUE_LIMIT = 48
LOCK = 55
PRES_POS, PRES_SPEED, PRES_LOAD = 56, 58, 60
PRES_VOLT, PRES_TEMP = 62, 63
PRES_CURRENT = 69

# Protecoes (EEPROM). Valores conservadores para a bancada; revisar depois da fase 7.
PROTECOES = {
    MAX_TEMP: 65,          # graus C (fabrica ~70)
    MAX_VOLT: 130,         # 13,0 V (unidade 0,1 V)
    MIN_VOLT: 90,          # 9,0 V: abaixo disso a fonte esta caindo
}
# Ombro: mais tempo antes da protecao de sobrecarga soltar o torque (o braco cairia). Unidade 10 ms.
PROT_TIME_OMBRO = 250     # 2,5 s


def _sinal(v, bit):
    return -(v & ((1 << bit) - 1)) if v & (1 << bit) else v


def _com_sinal(v, bit):
    return (abs(v) | (1 << bit)) if v < 0 else v


class Barramento:
    def __init__(self, porta):
        self.port = PortHandler(porta)
        self.ph = PacketHandler(0)          # STS = little endian
        if not self.port.openPort():
            sys.exit(f"Nao abriu {porta}")
        if not self.port.setBaudRate(BAUD):
            sys.exit("Nao ajustou a velocidade")

    def ok(self, res, err, oque):
        if res != COMM_SUCCESS:
            raise IOError(f"{oque}: {self.ph.getTxRxResult(res)}")
        if err:
            print(f"  aviso em {oque}: {self.ph.getRxPacketError(err)}")

    def ping(self, i):
        _, res, _ = self.ph.ping(self.port, i)
        return res == COMM_SUCCESS

    def w1(self, i, a, v):
        res, err = self.ph.write1ByteTxRx(self.port, i, a, v); self.ok(res, err, f"ID {i} @{a}")

    def w2(self, i, a, v):
        res, err = self.ph.write2ByteTxRx(self.port, i, a, v); self.ok(res, err, f"ID {i} @{a}")

    def r1(self, i, a):
        v, res, err = self.ph.read1ByteTxRx(self.port, i, a); self.ok(res, err, f"ID {i} @{a}"); return v

    def r2(self, i, a):
        v, res, err = self.ph.read2ByteTxRx(self.port, i, a); self.ok(res, err, f"ID {i} @{a}"); return v

    def eeprom(self, i, escritas):
        """Destrava, grava [(endereco, tamanho, valor)], trava de novo."""
        self.w1(i, LOCK, 0)
        for a, n, v in escritas:
            (self.w1 if n == 1 else self.w2)(i, a, v)
        self.w1(i, LOCK, 1)

    def procurar(self, ids=range(0, 21)):
        return [i for i in ids if self.ping(i)]


def cmd_procurar(b, a):
    achou = b.procurar()
    print("IDs que responderam:", achou or "nenhum (fonte ligada? jumper em B? porta certa?)")
    if achou.count(1) and len(achou) == 1:
        print("So o ID 1: pode ser um servo novo (todos saem de fabrica com ID 1).")


def cmd_id(b, a):
    achou = b.procurar()
    if achou != [a.de]:
        sys.exit(f"Precisa ter SO o servo {a.de} no barramento; respondendo: {achou}")
    if a.para not in NOMES:
        sys.exit("Use IDs de 1 a 6 (mapa no topo do arquivo)")
    b.eeprom(a.de, [(ID, 1, a.para)])
    time.sleep(0.1)
    print(f"ID {a.de} -> {a.para} ({NOMES[a.para]}).", "OK" if b.ping(a.para) else "NAO RESPONDE no novo ID!")
    print("Etiquete o servo com o numero antes de tirar do barramento.")


def cmd_ler(b, a):
    for i in a.ids:
        if not b.ping(i):
            print(f"ID {i} ({NOMES.get(i, '?')}): sem resposta"); continue
        pos = b.r2(i, PRES_POS)
        load = _sinal(b.r2(i, PRES_LOAD), 10) / 10.0
        volt = b.r1(i, PRES_VOLT) / 10.0
        temp = b.r1(i, PRES_TEMP)
        cur = b.r2(i, PRES_CURRENT) * 6.5 / 1000.0     # ~6,5 mA por unidade (conferir na bancada)
        ofs = _sinal(b.r2(i, OFFSET), 11)
        print(f"ID {i} ({NOMES.get(i, '?'):8s}) pos {pos:4d}  carga {load:+6.1f}%  {volt:4.1f} V  {temp:2d} C  ~{cur:4.2f} A  offset {ofs:+d}")


def cmd_protecoes(b, a):
    for i in a.ids:
        if not b.ping(i):
            print(f"ID {i}: sem resposta, pulei"); continue
        w = [(k, 1, v) for k, v in PROTECOES.items()]
        if i in (2, 3):
            w.append((PROT_TIME, 1, PROT_TIME_OMBRO))
        b.eeprom(i, w)
        print(f"ID {i} ({NOMES[i]}): protecoes gravadas")
    print("Limites de angulo NAO foram gravados: so depois da calibracao com o braco montado.")


def cmd_centro(b, a):
    print("Atencao: o servo vai se mover para 2048 devagar.")
    for i in a.ids:
        b.w1(i, ACCEL, 10)
        b.w2(i, GOAL_SPEED, 300)
        b.w2(i, GOAL_POS, b.r2(i, PRES_POS))   # alvo = posicao atual (sem pulo)
        b.w1(i, TORQUE_ENABLE, 1)
    sw = GroupSyncWrite(b.port, b.ph, GOAL_POS, 2)
    for i in a.ids:
        sw.addParam(i, [2048 & 0xFF, 2048 >> 8])
    sw.txPacket()
    time.sleep(2.0)
    cmd_ler(b, a)
    print("Torque continua ligado. Para soltar: comando 'soltar'.")


def cmd_soltar(b, a):
    for i in a.ids:
        if b.ping(i):
            b.w1(i, TORQUE_ENABLE, 0)
    print("Torque desligado.")


def cmd_ombro(b, a):
    """Mostra a carga dos 2 servos do ombro. Brigando = cargas altas com sinais opostos."""
    print("Ctrl+C para sair. Ajuste o offset do ID 3 ate as cargas ficarem parecidas.")
    try:
        while True:
            la = _sinal(b.r2(2, PRES_LOAD), 10) / 10.0
            lb = _sinal(b.r2(3, PRES_LOAD), 10) / 10.0
            # O B esta espelhado, entao quando os dois ajudam a segurar o braco as leituras tem
            # sinais OPOSTOS e modulos parecidos. Se os sinais ficarem IGUAIS e grandes (> ~20%)
            # com o braco parado, um empurra contra o outro: ajuste o offset do ID 3.
            print(f"\rA {la:+6.1f}%   B {lb:+6.1f}%   (A+B = {la + lb:+6.1f})   ", end="")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print()


def cmd_offset(b, a):
    atual = _sinal(b.r2(a.id, OFFSET), 11)
    novo = atual + a.passos
    if abs(novo) > 2047:
        sys.exit("Offset fora da faixa")
    b.eeprom(a.id, [(OFFSET, 2, _com_sinal(novo, 11))])
    print(f"ID {a.id}: offset {atual:+d} -> {novo:+d} passos ({novo * 360 / 4096:+.1f} graus)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--porta", required=True)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("procurar")
    x = s.add_parser("id"); x.add_argument("--de", type=int, default=1); x.add_argument("--para", type=int, required=True)
    for n in ("ler", "protecoes", "centro", "soltar"):
        x = s.add_parser(n); x.add_argument("--ids", type=int, nargs="+", default=list(NOMES))
    s.add_parser("ombro")
    x = s.add_parser("offset"); x.add_argument("--id", type=int, required=True); x.add_argument("--passos", type=int, required=True)
    a = p.parse_args()
    b = Barramento(a.porta)
    try:
        globals()["cmd_" + a.cmd](b, a)
    finally:
        b.port.closePort()


if __name__ == "__main__":
    main()
