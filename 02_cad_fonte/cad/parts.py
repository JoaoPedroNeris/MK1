"""
Pecas do MK I. Cada funcao devolve uma arvore CSG no referencial proprio da peca.

Referencial das juntas: eixo da junta na origem, eixo de giro em Y, elo
apontando para +X. O servo de cada junta mora no bolso do elo anterior,
com o corpo para tras (-X) e o horn nas faces +-Y.
"""
import numpy as np
from csg import Box, Cyl, CylX, CylY, Prism, U, stadium, chamfer_rect
from params import *


def bx(x0, x1, y0, y1, z0, z1, c=0.0):
    """Caixa por limites."""
    return Box(x1 - x0, y1 - y0, z1 - z0, c).move((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)


def hexbolt(x, y, z, axis="y", r=2.6, h=1.6):
    """Cabeca de parafuso decorativa/funcional."""
    c = Cyl(r, h, fn=6)
    if axis == "y":
        c = c.rot(90, 0, 0)
    elif axis == "x":
        c = c.rot(0, 90, 0)
    return c.move(x, y, z)


# ============================================================ bolso do servo
PX0 = POCKET_X0 - END_WALL_B     # face externa traseira
PX1 = POCKET_X1 + END_WALL_F     # face externa dianteira
XF = POCKET_X1 + END_WALL_F / 2  # inserto da frente da tampa do servo
XB = POCKET_X0 - END_WALL_B / 2  # insertos de tras da tampa do servo
XC = PX0 + END_WALL_B / 2        # inserto da tampa de baixo no bolso (relativo ao eixo)
PZ = BEAM_H / 2                  # bolso tem a mesma altura do braco


def _horn_clearance():
    """Folga para o horn girar nas faces +-Y do servo."""
    r = HORN_D / 2 + 1.0
    w = POCKET_Y + 2 - (SV_H / 2 - 0.25)
    yc = SV_H / 2 - 0.25 + w / 2
    return [CylY(r, w).move(0, yc, 0), CylY(r, w).move(0, -yc, 0)]


def _ridges(z0, z1):
    y0 = SV_H / 2 + TOL
    return [bx(POCKET_X0, POCKET_X1, y0, POCKET_Y, z0, z1),
            bx(POCKET_X0, POCKET_X1, -POCKET_Y, -y0, z0, z1)]


def _front_round():
    """v0.2c: ponta da frente arredondada em FRONT_R em volta do eixo (folga ate a ponte do garfo seguinte)."""
    big = 4 * (SV_L + END_WALL_B)
    return U(CylY(FRONT_R, big), bx(-big, 0, -big / 2, big / 2, -big / 2, big / 2))


def pocket():
    """Metade de baixo do bolso: fundo, paredes de ponta, frisos. Topo aberto."""
    body = bx(PX0, PX1, -POCKET_Y, POCKET_Y, -PZ, POCKET_Z, c=1.0) & _front_round()
    cavity = bx(POCKET_X0, POCKET_X1, -POCKET_Y - 1, POCKET_Y + 1, -POCKET_Z, POCKET_Z + 1)
    solid = (body - cavity) + U(*_ridges(-POCKET_Z, -POCKET_Z + RIDGE))
    cuts = _horn_clearance()
    # insertos M3 para a tampa
    for (x, y) in [(XF, 0.0), (XB, 12.0), (XB, -12.0)]:
        cuts.append(Cyl(INSERT_M3 / 2, 9).move(x, y, POCKET_Z - 4.5))
    # saida do cabo do servo pela parede traseira
    cuts.append(bx(PX0 - 1, POCKET_X0 + 1, CABLE_SLOT_Y[0], CABLE_SLOT_Y[1], -POCKET_Z, -POCKET_Z + 8))
    for c in cuts:
        solid = solid - c
    return solid


def servo_cap():
    """Tampa do bolso (metade de cima). A mesma peca serve para os 4 bolsos (2 do ombro, cotovelo, punho): imprimir 4."""
    body = bx(PX0, PX1, -POCKET_Y, POCKET_Y, POCKET_Z, PZ, c=1.5) & _front_round()
    # v0.2d: frisos sobem 1,5 mm para dentro do corpo; antes o chanfro c=1,5 da borda de baixo
    # comia a largura toda do friso (1,5 mm) e ele so encostava numa linha (soltava na impressao)
    solid = body + U(*_ridges(POCKET_Z - RIDGE, POCKET_Z + 1.5))
    for (x, y) in [(XF, 0.0), (XB, 12.0), (XB, -12.0)]:
        solid = solid - Cyl(SCREW_M3 / 2, 12).move(x, y, PZ - 2)
        if x == XB:   # v0.2c: so atras; na frente a ponta arredondada nao deixa parede para o rebaixo
            solid = solid - Cyl(3.2, 2.0).move(x, y, PZ)      # rebaixo da cabeca
    # nervuras de estilo no topo
    for y in (-7.0, 7.0):
        solid = solid + bx(POCKET_X0 + 4, POCKET_X1 - 3, y - 1.2, y + 1.2, PZ - 0.5, PZ + 1.2, c=0.5)
    for c in _horn_clearance():
        solid = solid - c
    return solid


# ============================================================ garfo + ponte
def clevis(off=0.0):
    """Duas placas que aparafusam nos horns do servo anterior, unidas por uma ponte.
    off > 0: junta com 2 servos lado a lado (ombro v0.2); cada placa pega o horn de fora de um servo."""
    plates = []
    for s in (1, -1):
        yc = s * (off + CLV_IN + CLV_T / 2)
        p = CylY(CLV_R, CLV_T).move(0, yc, 0) + bx(0, BRIDGE_X1, yc - CLV_T / 2, yc + CLV_T / 2,
                                                   -BEAM_H / 2, BEAM_H / 2, c=1.0)
        plates.append(p)
    ymax = off + CLV_IN + CLV_T
    bridge = bx(BRIDGE_X0, BRIDGE_X1 + 2, -ymax, ymax, -BEAM_H / 2, BEAM_H / 2, c=2.0)
    solid = U(*plates, bridge)
    # furos do horn (4 no circulo + centro) nas duas placas
    yl = 2 * (off + CLV_IN + CLV_T) + 2      # v0.2c: soma o afastamento do ombro duplo (antes faltavam os furos)
    solid = solid - CylY(HORN_CTR / 2, yl)
    for a in (45, 135, 225, 315):
        x = HORN_PCD / 2 * np.cos(np.radians(a))
        z = HORN_PCD / 2 * np.sin(np.radians(a))
        solid = solid - CylY(HORN_HOLE / 2, yl).move(x, 0, z)
    # passagem de cabos pela ponte
    solid = solid - bx(BRIDGE_X0 - 1, BRIDGE_X1 + 3, -7, 7, -5, 5)
    # v0.2: na garra, o garfo do punho e a caixa do servo da garra sao uma peca so (modelada no Fusion: garra_base)
    return solid


# ============================================================ elos do braco
def _beam(x0, x1):
    outer = bx(x0, x1, -POCKET_Y, POCKET_Y, -BEAM_H / 2, BEAM_H / 2, c=BEAM_C)
    channel = bx(x0 - 1, x1 + 1, -POCKET_Y + WALL, POCKET_Y - WALL, -BEAM_H / 2 - 1, BEAM_H / 2 - WALL)
    return outer - channel


def _armor_recess(x0, x1):
    cuts = []
    for s in (1, -1):
        cuts.append(bx(x0, x1, s * POCKET_Y - 0.8, s * POCKET_Y + 0.8, -BEAM_H / 2 + 6, BEAM_H / 2 - 6))
    return cuts


def armor_span(L):
    return BRIDGE_X1 + 6, L + PX0 - 3


def link(L, spring_lug=False, off=0.0):
    """Elo generico: garfo na junta proximal, viga em U, bolso do servo na junta distal."""
    beam = _beam(BRIDGE_X1, L + PX0 + 1)
    solid = U(clevis(off), beam, pocket().move(L, 0, 0))
    # fechamento da viga junto a ponte e insertos da tampa de baixo
    solid = solid + bx(BRIDGE_X1, BRIDGE_X1 + CLOSE_L, -POCKET_Y, POCKET_Y, -BEAM_H / 2, BEAM_H / 2, c=1.0)
    solid = solid - bx(BRIDGE_X0 - 1, BRIDGE_X1 + CLOSE_L + 2, -7, 7, -5, 5)   # cabo segue pela viga
    for x in (BRIDGE_X1 + 3, L + XC):
        solid = solid - Cyl(INSERT_M3 / 2, INSERT_L + 0.8).move(x, 0, -BEAM_H / 2 + (INSERT_L + 0.8) / 2)
    if spring_lug:
        lug = bx(SPRING_B[0] - 10, SPRING_B[-1] + 10, -3, 3, BEAM_H / 2 - 1, BEAM_H / 2 + 12, c=1.5)
        solid = solid + lug
        for b in SPRING_B:
            solid = solid - CylY(1.8, 10).move(b, 0, BEAM_H / 2 + 6)
    a0, a1 = armor_span(L)
    for c in _armor_recess(a0, a1):
        solid = solid - c
    return solid


def upper_arm():
    return link(L1, off=SH_OFF)       # v0.2: sem mola, garfo largo para os 2 servos do ombro


def forearm():
    return link(L2)


def belly_cover(L):
    """Tampa de baixo do canal de cabos."""
    x0, x1 = BRIDGE_X1 - 2, L + XC + 5.5         # v0.2c: tampa vai ate depois do inserto do bolso
    plate = bx(x0, x1, -POCKET_Y + BEAM_C, POCKET_Y - BEAM_C, -BEAM_H / 2 - 3, -BEAM_H / 2, c=1.0)
    for x in (BRIDGE_X1 + 3, L + XC):
        plate = plate - Cyl(SCREW_M3 / 2, 8).move(x, 0, -BEAM_H / 2 - 1.5)
    # rasgos de ventilacao/estilo
    n = int((x1 - x0 - 20) // 9)
    for i in range(n):
        x = x0 + 14 + i * 9
        plate = plate - Prism(stadium(18, 3.4), 6).rot(0, 0, 90).move(x, 0, -BEAM_H / 2 - 1.5)
    # v0.2b: saida do cabo para o laco da junta, aberta para a borda +Y, logo depois de cada presilha.
    # A presilha usa o mesmo parafuso da tampa (M3 x 14 no lugar do curto), entao o braco nao muda.
    xs_p = BRIDGE_X1 + 3                      # parafuso da ponta do garfo
    xs_d = L + XC                             # parafuso da ponta do bolso
    yn = CABO_Y0 - 0.5
    for xa, xb in [(xs_p + CLIP_C / 2 + 0.5, xs_p + CLIP_C / 2 + 0.5 + NOTCH_L),
                   (xs_d - CLIP_C / 2 - 0.5 - NOTCH_L, xs_d - CLIP_C / 2 - 0.5)]:
        plate = plate - bx(xa, xb, yn, POCKET_Y + 1, -BEAM_H / 2 - 5, -BEAM_H / 2 + 1)
    return plate


def presilha_cabo():
    """Presilha do cabo do barramento: 1 parafuso M3. Tunel CABO_L x CABO_A com friso de aperto.
    Referencial: furo no eixo Z em (0,0), face de apoio em z=0, cabo correndo em X, tunel em +Y."""
    h = CABO_A + WALL
    y0, y1 = -CLIP_ABA / 2, CLIP_ABA / 2 + CABO_L + WALL
    body = bx(-CLIP_C / 2, CLIP_C / 2, y0, y1, 0, h, c=0.6)
    body = body - bx(-CLIP_C / 2 - 1, CLIP_C / 2 + 1, CLIP_ABA / 2, CLIP_ABA / 2 + CABO_L, -1, CABO_A)
    body = body + bx(-1.5, 1.5, CLIP_ABA / 2, CLIP_ABA / 2 + CABO_L, CABO_A - FRISO, CABO_A)
    return body - Cyl(SCREW_M3 / 2, 2 * h + 2)


def armor(L):
    """Placa laranja que cola (fita VHB) no rebaixo lateral da viga. Imprimir 2."""
    a0, a1 = armor_span(L)
    h = BEAM_H - 12 - 0.6
    plate = Prism(chamfer_rect(a1 - a0 - 0.6, h, 3.0), 2.0).rot(90, 0, 0)   # espessura em Y
    plate = plate.move((a0 + a1) / 2, 0, 0)
    xs = [a0 + 5, a1 - 5]
    for x in xs:
        for z in (h / 2 - 4, -h / 2 + 4):
            plate = plate + hexbolt(x, -1.6, z, axis="y", r=2.2, h=1.4)
    # sulcos horizontais
    for z in (-3.0, 3.0):
        plate = plate - bx(a0 + 10, a1 - 10, -1.6, -0.6, z - 0.6, z + 0.6)
    return plate


# ============================================================ torre
def turret():
    """v0.2: dois bolsos de servo lado a lado (ombro com 2 STS3215), sem coluna da mola."""
    tz = TURRET_T
    W = SH_OFF + POCKET_Y                       # meia largura do pedestal
    disk = Cyl(TURRET_R, tz).move(0, 0, tz / 2)
    hub = Cyl(14, 16).move(0, 0, -8)
    # v0.2c: frente do pedestal fica onde estava (POCKET_X1 + 6) para nao bater no garfo do braco descendo
    ped = bx(SHOULDER_X + PX0, SHOULDER_X + POCKET_X1 + 6.0, -W, W, tz, SHOULDER_Z - PZ + 0.5, c=2.0)
    plinth = bx(SHOULDER_X + PX0 - 6, SHOULDER_X + PX1 + 6, -W - 8, W + 8, tz - 0.5, tz + 8, c=3.0)
    pockets = [pocket().move(SHOULDER_X, s * SH_OFF, SHOULDER_Z) for s in (1, -1)]
    solid = U(disk, hub, ped, plinth, *pockets)
    # acoplamento ao horn do servo de giro (por baixo)
    solid = solid - Cyl(HORN_D / 2 + 0.3, 1.2).move(0, 0, -16 + 0.6)
    for a in (45, 135, 225, 315):
        x, y = HORN_PCD / 2 * np.cos(np.radians(a)), HORN_PCD / 2 * np.sin(np.radians(a))
        solid = solid - Cyl(PILOT_M3 / 2, 20).move(x, y, -16 + 10)
    # acesso ao parafuso central do horn (montar antes dos servos do ombro)
    solid = solid - Cyl(HORN_CTR / 2, 70).move(0, 0, 20)
    # rasgos para a placa de cima do lazy susan (diagonais)
    for a in (45, 135, 225, 315):
        r = 59.0
        solid = solid - Prism(stadium(14, 4.6), 12).rot(0, 0, a).move(r * np.cos(np.radians(a)),
                                                                      r * np.sin(np.radians(a)), tz / 2)
    # cabos: os 2 servos do ombro saem pela parede de tras, descem por um furo vertical ate a base
    zf = SHOULDER_Z - POCKET_Z
    xc = SHOULDER_X + (PX0 + POCKET_X0) / 2
    solid = solid - bx(SHOULDER_X + PX0 - 1, SHOULDER_X + POCKET_X0 + 1, -SH_OFF - 6, SH_OFF + 6, zf, zf + 8)
    solid = solid - Cyl(5, zf + 8 + 2).move(xc, 0, (zf + 8) / 2 - 1)
    # v0.2b: bloco da presilha do cabo do ombro, atras do pedestal, acima do rasgo dos cabos
    xr = SHOULDER_X + PX0
    tb = bx(xr + TCLIP_X[0], xr + TCLIP_X[1] + 0.5, TCLIP_Y[0], TCLIP_Y[1], TCLIP_Z0, TCLIP_Z0 + TCLIP_H, c=1.5)
    solid = solid + tb
    xi, yi = xr + (TCLIP_X[0] + TCLIP_X[1]) / 2, TCLIP_Y[0] + CLIP_ABA / 2 + 1.0
    solid = solid - Cyl(INSERT_M3 / 2, INSERT_L + 0.8).move(xi, yi, TCLIP_Z0 + TCLIP_H - (INSERT_L + 0.8) / 2 + 0.01)
    return solid


# ============================================================ base
SH_IN = WALL
YAW_TOP = SHELL_Z + ACRYLIC + LS_T - 16 - HORN_T   # topo do servo de giro, no referencial da carcaca
YAW_BOT = YAW_TOP - SV_H
ESTOP_XY = (68.0, -60.0)
UNO_O = (-76.0, 18.0)
UNO_HOLES = [(13.97, 2.54), (15.24, 50.8), (66.04, 7.62), (66.04, 35.56)]


def lid_corners():
    """Colunas dos parafusos da tampa/placa. v0.2: a da frente-direita sai do canto para dar
    lugar ao bloco de contato do botao de emergencia, que fica embaixo da tampa."""
    cx, cy = SHELL_X / 2 - WALL - 4, SHELL_Y / 2 - WALL - 4
    return [(cx, cy), (-cx, cy), (-cx, -cy), (cx, ESTOP_XY[1] + 24)]


def base_shell():
    X, Y, Z = SHELL_X / 2, SHELL_Y / 2, SHELL_Z
    outer = bx(-X, X, -Y, Y, 0, Z, c=4.0)
    inner = bx(-X + WALL, X - WALL, -Y + WALL, Y - WALL, WALL, Z + 1)
    solid = outer - inner
    # cantos para os parafusos da tampa
    adds = []
    for (px, py) in lid_corners():
        adds.append(Cyl(5.5, Z - WALL).move(px, py, WALL + (Z - WALL) / 2))   # v0.2c: raio 5 -> 5,5
    # berco do servo de giro (corpo para -X, eixo no centro)
    x0, x1 = POCKET_X0, POCKET_X1
    zt = YAW_BOT + 25
    adds.append(bx(x0 - WALL, x1 + WALL, -SV_W / 2 - TOL - WALL, SV_W / 2 + TOL + WALL, WALL, zt, c=1.5))
    # suportes do Arduino UNO
    for hx, hy in UNO_HOLES:
        adds.append(Cyl(3.2, 6).move(UNO_O[0] + hx, UNO_O[1] + hy, WALL + 3))
    solid = U(solid, *adds)
    cuts = [bx(x0, x1, -SV_W / 2 - TOL, SV_W / 2 + TOL, YAW_BOT, zt + 1),
            bx(x0 - WALL - 1, x0 + 1, -6, 6, YAW_BOT, YAW_BOT + 8)]
    for (px, py) in lid_corners():
        cuts.append(Cyl(INSERT_M3 / 2, 10).move(px, py, Z - 5))
        cuts.append(Cyl(INSERT_M3 / 2, 16).move(px, py, 0))     # parafusos da placa de base
    for hx, hy in UNO_HOLES:
        cuts.append(Cyl(PILOT_M3 / 2, 10).move(UNO_O[0] + hx, UNO_O[1] + hy, WALL + 4))
    # painel traseiro: conector 12 V e passagem dos USB
    cuts.append(CylX(6.0, 10).move(-X, -40, 26))
    cuts.append(bx(-X - 2, -X + WALL + 2, 40, 62, 19, 33))
    # ventilacao nas laterais
    for s in (1, -1):
        for x in (-62, -50, -38, 38, 50, 62):
            cuts.append(Prism(stadium(24, 4.2), 10).rot(0, 0, 90).rot(90, 0, 0).move(x, s * Y, 30))
    # frisos horizontais de estilo na frente
    for z in (14, 20):
        cuts.append(bx(X - 1, X + 1, -Y + 20, Y - 20, z - 0.8, z + 0.8))
    for c in cuts:
        solid = solid - c
    return solid


# ---- pecas 2D de corte a laser (mesma descricao gera SVG e 3D)
def lid_2d():
    X, Y = SHELL_X / 2, SHELL_Y / 2
    holes = [(px, py, SCREW_M3) for (px, py) in lid_corners()]
    holes.append((0.0, 0.0, 62.0))   # v0.2: maior, o furo de cabos da torre fica a r=25,7
    holes.append((ESTOP_XY[0], ESTOP_XY[1], ESTOP_D))
    slots = [(59 * np.cos(np.radians(a)), 59 * np.sin(np.radians(a)), 14, 4.6, a) for a in (0, 90, 180, 270)]
    for x in (-82.0, -74.0):
        for y in (-36.0, 0.0, 36.0):
            slots.append((x, y, 24, 4.2, 90))
    text = [("MK I", 58, 52, 12), ("EMERG.", ESTOP_XY[0], ESTOP_XY[1] + 17, 5)]
    return dict(outline=chamfer_rect(SHELL_X, SHELL_Y, 4.0), holes=holes, slots=slots, text=text,
                thick=ACRYLIC, color="laranja")


def plate_2d():
    xc = (-SHELL_X / 2 - PLATE_TAIL + SHELL_X / 2) / 2
    w = SHELL_X + PLATE_TAIL
    outline = chamfer_rect(w, SHELL_Y, 8.0) + np.array([xc, 0])
    holes = [(px, py, SCREW_M3) for (px, py) in lid_corners()]
    mx = -SHELL_X / 2 - PLATE_TAIL / 2 + 2   # v0.2: sem mastro, a cauda fica so para os grampos
    text = [("GRAMPO", -SHELL_X / 2 - 50, 57, 5), ("GRAMPO", -SHELL_X / 2 - 50, -57, 5)]
    marks = [(-SHELL_X / 2 - 50, s * 57, 26, 26) for s in (1, -1)]
    return dict(outline=outline, holes=holes, slots=[], text=text, marks=marks, thick=ACRYLIC,
                color="preto", mast_xy=(mx, 0.0))


def solid_from_2d(d):
    t = d["thick"]
    s = Prism(d["outline"], t).move(0, 0, t / 2)
    for x, y, dia in d["holes"]:
        s = s - Cyl(dia / 2, t + 2).move(x, y, t / 2)
    for x, y, ln, w, a in d["slots"]:
        s = s - Prism(stadium(ln, w), t + 2).rot(0, 0, a).move(x, y, t / 2)
    return s


def base_lid():
    return solid_from_2d(lid_2d())


def base_plate():
    return solid_from_2d(plate_2d())


# ============================================================ mao
def _knuckle(fy, fz):
    parts = []
    for s in (1, -1):
        yc = fy + s * (TONGUE / 2 + 0.25 + 1.75)
        parts.append(bx(PALM_X1 - 1, KNUCKLE_X, yc - 1.75, yc + 1.75, fz - 5, fz + 5))
        parts.append(CylY(5, 3.5).move(KNUCKLE_X, yc, fz))
    return U(*parts)


FINGER_SERVOS = [(68.9, +18.0, False), (68.9, -18.0, False), (68.9, 0.0, True)]  # (x do eixo, y, invertido?)


def palm():
    body = bx(PALM_X0, PALM_X1, -PALM_Y, PALM_Y, -PALM_Z, PALM_Z, c=4.0)
    cav = bx(PALM_X0 + PALM_WALL, PALM_X1 - PALM_WALL, -PALM_Y + PALM_WALL, PALM_Y - PALM_WALL,
             -PALM_Z + PALM_WALL, PALM_Z + 1)
    solid = body - cav
    ix0, ix1 = PALM_X0 + PALM_WALL - 0.1, PALM_X1 - PALM_WALL + 0.1
    iy = PALM_Y - PALM_WALL + 0.1
    floor = -PALM_Z + PALM_WALL
    # prateleira dos 2 servos dos dedos e ponte do servo do polegar (invertido)
    shelf_top = floor + 0.5 + MS_EAR_Z
    shelf = bx(ix0, ix1, -iy, iy, shelf_top - 2.5, shelf_top)
    thumb_top = PALM_Z - 0.5                           # face de baixo do servo, virada para cima
    th_ear = thumb_top - MS_EAR_Z
    bridge = bx(ix0, ix1, -9, 9, th_ear, th_ear + 2.5)
    bosses = [Cyl(3.5, 2 * PALM_Z - PALM_WALL).move(x, y, PALM_WALL / 2)
              for x in (PALM_X0 + 4.5, PALM_X1 - 4.5) for y in (PALM_Y - 4.5, -PALM_Y + 4.5)]
    solid = U(solid, shelf, bridge, *bosses, *[_knuckle(fy, fz) for fy, fz, _ in FINGERS], clevis())
    cuts = []
    for sx, sy, inv in FINGER_SERVOS:
        x0 = sx + MS_SHAFT_X - MS_L
        cuts.append(bx(x0 - TOL, x0 + MS_L + TOL, sy - MS_W / 2 - TOL, sy + MS_W / 2 + TOL, floor + 0.1, PALM_Z + 1))
        for ex in (x0 - 2.4, x0 + MS_L + 2.4):     # furos das orelhas (M2)
            zc = th_ear + 1.25 if inv else shelf_top - 1.25
            cuts.append(Cyl(0.9, 6).move(ex, sy, zc))
    for x in (PALM_X0 + 4.5, PALM_X1 - 4.5):
        for y in (PALM_Y - 4.5, -PALM_Y + 4.5):
            cuts.append(Cyl(PILOT_M3 / 2 - 0.1, 12).move(x, y, PALM_Z - 5))
    for fy, fz, thumb in FINGERS:
        s = 1 if thumb else -1                   # lado palmar
        cuts.append(CylY(PIN_D / 2, FW + 4).move(KNUCKLE_X, fy, fz))
        cuts.append(CylX(1.1, 10).move(PALM_X1 - 1, fy, fz + s * 3.5))     # tendao
        cuts.append(CylX(1.1, 10).move(PALM_X1 - 1, fy, fz - s * 3.5))     # elastico de retorno
    for c in cuts:
        solid = solid - c
    return solid


def palm_lid():
    z0 = PALM_Z
    t = 2.4
    lid = bx(PALM_X0, PALM_X1, -PALM_Y, PALM_Y, z0, z0 + t, c=1.2)
    # suporte do sensor ultrassonico HC-SR04 (do kit) olhando para frente
    bracket = bx(PALM_X1 - 6, PALM_X1 - 2, -25, 25, z0 + t - 0.5, z0 + t + 24, c=1.0)
    gussets = [Prism([(0, 0), (10, 0), (0, 12)], 3).rot(90, 0, 0).rot(0, 0, 180).move(PALM_X1 - 6, y, z0 + t)
               for y in (-22.0, 22.0)]
    ribs = [bx(PALM_X0 + 6, PALM_X1 - 26, y - 1.5, y + 1.5, z0 + t - 0.5, z0 + t + 2.0, c=0.6)
            for y in (-20.0, -10.0, 0.0, 10.0, 20.0)]
    solid = U(lid, bracket, *gussets, *ribs)
    for x in (PALM_X0 + 4.5, PALM_X1 - 4.5):
        for y in (PALM_Y - 4.5, -PALM_Y + 4.5):
            solid = solid - Cyl(SCREW_M3 / 2, 8).move(x, y, z0 + t / 2)
            solid = solid - Cyl(2.6, 1.2).move(x, y, z0 + t)
    for y in (-13.0, 13.0):
        solid = solid - CylX(8.4, 10).move(PALM_X1 - 4, y, z0 + t + 12.5)
    solid = solid - bx(PALM_X0 + 10, PALM_X0 + 22, -6, 6, z0 - 1, z0 + t + 1)    # cabos do sensor
    return solid


def _tongue():
    return CylY(5, TONGUE) + bx(0, 6, -TONGUE / 2, TONGUE / 2, -5, 5)


def finger_proximal():
    body = bx(5, PH1 - 2, -FW / 2, FW / 2, -FT / 2, FT / 2, c=1.5)
    cheeks = [CylY(5.5, (FW - TONGUE) / 2 - 0.25).move(PH1, s * (FW / 2 - ((FW - TONGUE) / 2 - 0.25) / 2), 0)
              for s in (1, -1)]
    solid = U(_tongue(), body, *cheeks)
    solid = solid - bx(PH1 - 8.5, PH1 + 7, -TONGUE / 2 - 0.25, TONGUE / 2 + 0.25, -8, 8)
    solid = solid - CylY(PIN_D / 2 + 0.15, TONGUE + 2)
    solid = solid - CylY(PIN_D / 2, FW + 2).move(PH1, 0, 0)
    solid = solid - CylX(0.8, PH1 + 14).move(PH1 / 2, 0, -3.5)       # tendao (lado palmar)
    solid = solid - CylX(1.0, PH1 + 14).move(PH1 / 2, 0, 3.5)        # elastico (dorso)
    for x in (12.0, 22.0):                                            # frisos de estilo no dorso
        solid = solid - bx(x - 0.6, x + 0.6, -FW / 2 - 1, FW / 2 + 1, FT / 2 - 0.8, FT / 2 + 1)
    return solid


def finger_distal():
    body = bx(5, PH2 - 6, -FW / 2, FW / 2, -FT / 2, FT / 2, c=1.5)
    tip = CylY(FT / 2, FW).move(PH2 - 6, 0, 0)
    solid = U(_tongue(), body, tip)
    solid = solid - CylY(PIN_D / 2 + 0.15, TONGUE + 2)
    solid = solid - bx(8, PH2 - 3, -5.2, 5.2, -FT / 2 - 1, -FT / 2 + 1.2)   # rebaixo da almofada
    solid = solid - CylX(0.8, PH2).move((PH2 - 9) / 2 - 1, 0, -3.5)
    solid = solid - CylX(1.0, PH2).move((PH2 - 9) / 2 - 1, 0, 3.5)
    solid = solid - CylY(0.8, FW + 2).move(PH2 - 9, 0, -3.5)          # amarracao do tendao
    solid = solid - CylY(1.0, FW + 2).move(PH2 - 9, 0, 3.5)
    return solid


def finger_pad():
    """Almofada de TPU colada no rebaixo da falange distal."""
    ln = PH2 - 11 - 0.4
    pad = bx(-ln / 2, ln / 2, -5.0, 5.0, 0, 2.2, c=0.6)
    for i in range(5):
        x = -ln / 2 + 2.5 + i * (ln - 5) / 4
        pad = pad + bx(x - 0.6, x + 0.6, -4.4, 4.4, 2.0, 2.8)
    return pad


def spool():
    s = U(Cyl(6, 6.2), Cyl(9, 1.2).move(0, 0, 3.6), Cyl(9, 1.2).move(0, 0, -3.6))
    s = s - Cyl(1.25, 12)
    s = s - bx(-10, 10, -2.9, 2.9, -4.3, -4.3 + 1.6)                 # encaixe do horn de 1 braco (MEDIR)
    s = s - CylX(0.8, 14).move(0, 0, 1.0)                             # amarracao do tendao
    return s


# ============================================================ mastro da camera
def mast_socket():
    h = 46.0
    s = bx(-20, 20, -20, 20, 0, h, c=3.0)
    s = s - Cyl(POLE_D / 2 + 0.3, h).move(0, 0, h / 2 + 6)
    s = s - CylX(INSERT_M3 / 2, 14).move(13, 0, 32)                    # inserto M3 do parafuso de trava do mastro
    for sx in (1, -1):
        for sy in (1, -1):
            s = s - Cyl(SCREW_M3 / 2, 20).move(sx * 13, sy * 13, 5)
            s = s - Cyl(4.2, h).move(sx * 13, sy * 13, h / 2 + 8)
    for z in (14.0, 22.0):
        s = s - bx(19, 21, -14, 14, z - 0.8, z + 0.8)
    return s


def mast_head():
    collar = Cyl(16, 34)
    arm = bx(12, 112, -8, 8, 4, 17, c=2.0)
    ears = bx(-27, -12, -7, 7, -14, 14, c=1.5)
    fork = [bx(104, 124, 4.2, 8.2, -6, 17, c=1.0), bx(104, 124, -8.2, -4.2, -6, 17, c=1.0)]
    knobs = [CylY(8, 4).move(118, s * 6.2, 2) for s in (1, -1)]
    s = U(collar, arm, ears, *fork, *knobs)
    s = s - Cyl(POLE_D / 2 + 0.3, 40)
    s = s - bx(-30, -8, -1.2, 1.2, -20, 20)                          # rasgo da abracadeira
    s = s - CylY(SCREW_M3 / 2, 20).move(-20, 0, 0)
    s = s - CylY(SCREW_M3 / 2, 20).move(118, 0, 2)                   # eixo de inclinacao M3
    return s


def camera_plate():
    tongue = bx(-6, 6, -4, 4, -24, 0) + CylY(6, 8)
    plate = bx(-26, 26, -18, 18, -28, -24, c=1.5)
    s = U(tongue, plate)
    s = s - CylY(SCREW_M3 / 2, 12)
    s = s - Prism(stadium(14, 6.6), 8).move(4, 0, -26)               # parafuso 1/4"-20 da webcam (unica excecao ao M3, se a webcam tiver rosca de tripe)
    return s


# ============================================================ cupom de teste (v0.2, so M3)
def fit_coupon():
    """12 furos em ordem, da esquerda para a direita (sem paquimetro: conte os furos).
    1-3 inserto M3 | 4-6 passante M3 (e pino da garra) | 7-9 piloto M3 autoatarraxante | 10-12 mastro 3/4"."""
    plate = bx(0, 172, 0, 35, 0, 6, c=1.0)
    holes = []
    x = 8.0
    rows = [("inserto M3", (4.0, 4.2, 4.4)), ("passante M3", (3.2, 3.4, 3.6)), ("piloto M3", (2.4, 2.6, 2.8))]
    for _, ds in rows:
        for d in ds:
            holes.append(Cyl(d / 2, 10).move(x, 9, 3))
            x += 8.0
        x += 6.0
    for i, d in enumerate((POLE_D + 0.2, POLE_D + 0.4, POLE_D + 0.6)):
        holes.append(Cyl(d / 2, 14).move(30 + i * 30, 50, 5))      # passantes (v0.1 era cego)
    pole_block = bx(10, 110, 34, 66, 0, 10, c=1.0)
    ring_x0, ring_x1 = 118.0, 118.0 + (POCKET_X1 - POCKET_X0) + 2 * WALL
    ring = bx(ring_x0, ring_x1, 34, 66, 0, 10)
    s = U(plate, pole_block, ring)
    s = s - bx(ring_x0 + WALL, ring_x1 - WALL, 50 - POCKET_Z, 50 + POCKET_Z, -1, 11)
    for h in holes:
        s = s - h
    return s
