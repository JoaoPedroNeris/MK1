# 06_software: bancada do MK I (19/11/2026)

**Nada daqui foi testado com hardware ainda.** Foi escrito antes dos servos chegarem. Use primeiro com um servo solto na mesa.

| Arquivo | Para que serve |
|---|---|
| `servos/configurar_servos.py` | Procurar servos, trocar o ID (um por vez no barramento), ler posição, carga, tensão e temperatura, gravar as proteções, levar ao centro (2048), soltar o torque, monitorar o ombro duplo e ajustar o offset do ombro B. Instalar com `pip install feetech-servo-sdk pyserial`. O uso de cada comando está no topo do arquivo. |
| `arduino/mk1_energia/mk1_energia.ino` | Relé dos 12 V (só liga com "ARMAR" e com o e-stop solto), detecção do e-stop pelo divisor no A0 e botão PARAR no D2. Abra na IDE do Arduino e grave no UNO. |

## Ordem na fase 1 (bancada)

1. Grave o sketch no UNO. **Sem servos**, ligue a fonte e abra o Monitor Serial em 115200. Deve aparecer `v12=12.0` com o e-stop solto e `estop=1` com ele apertado. Mande `ARMAR`: o relé clica, e os 12 V aparecem no borne da Waveshare (confira no multímetro). Aperte o e-stop: deve aparecer `EVENTO ESTOP`, e o relé abre.
2. Ligue **um** servo e rode `procurar`, depois `id --de 1 --para N`. Etiquete o servo e repita para os 6.
3. Rode `protecoes` com todos ligados e depois `ler`.
4. Antes de montar o garfo do ombro, rode `centro --ids 2 3` (fase 5 do checklist).

Mapa de IDs: 1 giro, 2 ombro A, 3 ombro B (espelhado), 4 cotovelo, 5 punho, 6 garra.
