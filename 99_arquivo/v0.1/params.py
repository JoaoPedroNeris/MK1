"""
Parametros do MK I. Tudo em milimetros.

Linhas marcadas MEDIR vieram de ficha tecnica ou estimativa: confira com
paquimetro na peca real antes de imprimir e ajuste aqui. Rode build.py de novo
e todas as pecas se atualizam.
"""

# ---------------- folgas de fabricacao (ajuste depois do cupom de teste)
TOL = 0.25          # folga por face em encaixes
WALL = 3.2          # parede estrutural (4 perimetros de 0,4 mm em PETG)
INSERT_M3 = 4.2     # furo para inserto roscado M3 a quente
SCREW_M3 = 3.4      # furo passante M3
SCREW_M25 = 2.8     # furo passante M2,5
PILOT_M25 = 2.2     # furo guia para parafuso M2,5 autoatarraxante
PIN_D = 2.0         # pinos das articulacoes dos dedos (aco 2 mm ou filamento 1,75)

# ---------------- servo de barramento Feetech STS3215 (12 V)
SV_L, SV_W, SV_H = 45.2, 24.7, 35.0   # comprimento, espessura, altura no eixo do eixo de saida
SV_SHAFT_END = 11.0                   # MEDIR: centro do eixo ate a ponta mais proxima
SV_MASS = 55.0                        # g, MEDIR
HORN_D, HORN_T = 22.0, 3.5            # MEDIR: disco do horn
HORN_PCD = 14.0                       # MEDIR: diametro do circulo dos 4 furos do horn
HORN_HOLE = SCREW_M25

# ---------------- microservo MG90S (dedos)
MS_L, MS_W, MS_H = 22.8, 12.2, 28.5   # MEDIR
MS_EAR_SPAN, MS_EAR_Z = 32.5, 16.0    # MEDIR: largura com orelhas, altura das orelhas desde o fundo
MS_SHAFT_X = 5.9                      # MEDIR: eixo ate a ponta mais proxima
MS_MASS = 13.4

# ---------------- bolso do servo (igual na torre, braco e antebraco)
RIDGE = 1.0                           # friso que impede o servo de deslizar no eixo Y
POCKET_X0 = -(SV_L - SV_SHAFT_END) - TOL   # interior, atras do eixo
POCKET_X1 = SV_SHAFT_END + TOL             # interior, a frente do eixo
POCKET_Z = SV_W / 2 + TOL
END_WALL = 6.0                        # paredes de ponta grossas para insertos M3
POCKET_Y = SV_H / 2 + TOL + 1.5       # meia largura externa do bolso

# ---------------- garfo (clevis) que abraca o servo da junta anterior
CLV_IN = SV_H / 2 + HORN_T            # face interna da placa encosta no horn
CLV_T = 5.0
CLV_R = 24.0
BRIDGE_X0, BRIDGE_X1 = 26.0, 34.0

# ---------------- elos
BEAM_W = 2 * POCKET_Y                 # largura do braco (Y)
BEAM_H = 34.0                         # altura do braco (Z)
BEAM_C = 3.0                          # chanfro
L1 = 160.0                            # ombro -> cotovelo
L2 = 150.0                            # cotovelo -> punho

# ---------------- base e torre
SHELL_X, SHELL_Y, SHELL_Z = 180.0, 160.0, 55.0
ACRYLIC = 6.35                        # chapa de 1/4"
PLATE_TAIL = 75.0                     # cauda da placa para os grampos
LS_SIZE, LS_T, LS_HOLE = 102.0, 8.0, 63.0  # MEDIR: rolamento lazy susan de 4"
TURRET_R, TURRET_T = 66.0, 6.0          # disco cobre os cantos do lazy susan
SHOULDER_X, SHOULDER_Z = 12.0, 56.0   # eixo do ombro no referencial da torre
POST_X = -32.0                        # coluna da mola (centro), relativo ao eixo de giro
SPRING_PX = -22.0                     # furos da barra da mola: X relativo ao eixo do ombro
SPRING_A = (34.0, 42.0)               # furos da barra: altura acima do eixo do ombro
SPRING_B = (70.0, 85.0, 100.0)        # furos no braco: distancia ao longo do braco
# Mola escolhida por analysis.py: ~60 mm livre, 0,3-0,4 N/mm, tensao inicial 4-6 N, ate ~130 mm
ESTOP_D = 22.5                        # botao de emergencia de 22 mm

# ---------------- mao
PALM_X0, PALM_X1 = BRIDGE_X1, 86.0
PALM_Y, PALM_Z = 33.0, 23.0           # meias medidas externas
PALM_WALL = 2.4
KNUCKLE_X = PALM_X1 + 6.0
FINGERS = [(+16.0, +11.0, False), (-16.0, +11.0, False), (0.0, -11.0, True)]  # (y, z, polegar?)
PH1, PH2 = 34.0, 26.0                 # falanges: proximal e distal (pino a pino / pino a ponta)
FW, FT = 14.0, 12.0                   # largura e espessura do dedo
TONGUE = 6.5

# ---------------- mastro da camera
POLE_D = 19.05                        # cavilha ou tubo de 3/4"
POLE_LEN = 450.0
