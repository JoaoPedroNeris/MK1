"""
Montagem do MK I: lista de pecas, materiais e posicao de cada uma numa pose.
"""
import numpy as np
from csg import Node, Box, Cyl, CylX, CylY, U, _rot_matrix
import parts as P
from params import *

# cores (RGB 0-1)
BLACK = (0.075, 0.075, 0.085)
ORANGE = (1.0, 0.40, 0.03)
ORANGE_ACR = (1.0, 0.36, 0.02)
TPU = (0.95, 0.36, 0.05)
SERVO = (0.13, 0.13, 0.145)
METAL = (0.62, 0.63, 0.66)
RED = (0.78, 0.05, 0.04)
YELLOW = (0.95, 0.72, 0.05)
PCB = (0.06, 0.22, 0.55)
WOOD = (0.42, 0.40, 0.38)

# nome -> (funcao, quantidade, processo, material, densidade g/cm3, fator de preenchimento, cor)
PARTS = {
    "base_plate":      (P.base_plate, 1, "Corte a laser", "Acrilico preto 1/4\"", 1.19, 1.0, BLACK),
    "base_lid":        (P.base_lid, 1, "Corte a laser", "Acrilico laranja 1/4\"", 1.19, 1.0, ORANGE_ACR),
    "base_shell":      (P.base_shell, 1, "FDM", "PETG preto", 1.27, 0.55, BLACK),
    "turret":          (P.turret, 1, "FDM", "PETG preto", 1.27, 0.55, BLACK),
    "servo_cap":       (P.servo_cap, 4, "FDM", "PETG preto", 1.27, 0.7, BLACK),
    "upper_arm":       (P.upper_arm, 1, "FDM", "PETG preto", 1.27, 0.55, BLACK),
    "upper_cover":     (lambda: P.belly_cover(L1), 1, "FDM", "PETG preto", 1.27, 0.8, BLACK),
    "upper_armor":     (lambda: P.armor(L1), 2, "FDM", "PETG laranja", 1.27, 0.9, ORANGE),
    "forearm":         (P.forearm, 1, "FDM", "PETG preto", 1.27, 0.55, BLACK),
    "fore_cover":      (lambda: P.belly_cover(L2), 1, "FDM", "PETG preto", 1.27, 0.8, BLACK),
    "fore_armor":      (lambda: P.armor(L2), 2, "FDM", "PETG laranja", 1.27, 0.9, ORANGE),
    "presilha_cabo":   (P.presilha_cabo, 7, "FDM", "PETG preto", 1.27, 1.0, BLACK),
    "palm":            (P.palm, 1, "FDM", "PETG preto", 1.27, 0.65, BLACK),
    "palm_lid":        (P.palm_lid, 1, "FDM", "PETG laranja", 1.27, 0.8, ORANGE),
    "finger_proximal": (P.finger_proximal, 3, "Resina", "Resina resistente preta", 1.15, 1.0, BLACK),
    "finger_distal":   (P.finger_distal, 3, "Resina", "Resina resistente preta", 1.15, 1.0, BLACK),
    "finger_pad":      (P.finger_pad, 3, "FDM", "TPU 95A laranja", 1.21, 1.0, TPU),
    "spool":           (P.spool, 3, "Resina", "Resina resistente", 1.15, 1.0, BLACK),
    "mast_socket":     (P.mast_socket, 1, "FDM", "PETG preto", 1.27, 0.55, BLACK),
    "mast_head":       (P.mast_head, 1, "FDM", "PETG laranja", 1.27, 0.55, ORANGE),
    "camera_plate":    (P.camera_plate, 1, "FDM", "PETG preto", 1.27, 0.7, BLACK),
    "fit_coupon":      (P.fit_coupon, 1, "FDM", "PETG", 1.27, 1.0, BLACK),
}

_cache = {}


def part(name):
    if name not in _cache:
        _cache[name] = PARTS[name][0]()
    return _cache[name]


class Ref(Node):
    """Referencia a uma peca: vira name(); no OpenSCAD e delega a geometria."""

    def __init__(self, name, node=None):
        self.name = name
        self.node = node if node is not None else part(name)

    def aabb(self):
        return self.node.aabb()

    def sdf(self, p):
        return self.node.sdf(p)

    def scad(self, ind=""):
        return f"{ind}{self.name}();"


# ---------------- hardware comprado (so para previa e massa)
def sts3215(side=0):
    """side=+1/-1: so o horn daquele lado (ombro duplo: o horn de dentro NAO e montado)."""
    body = P.bx(-(SV_L - SV_SHAFT_END), SV_SHAFT_END, -SV_H / 2, SV_H / 2, -SV_W / 2, SV_W / 2, c=1.5)
    hp = CylY(HORN_D / 2, HORN_T).move(0, SV_H / 2 + HORN_T / 2, 0)
    hn = CylY(HORN_D / 2, HORN_T).move(0, -SV_H / 2 - HORN_T / 2, 0)
    horns = hp if side > 0 else hn if side < 0 else U(hp, hn)
    return body, horns


def sts3215_vertical():
    body = P.bx(-(SV_L - SV_SHAFT_END), SV_SHAFT_END, -SV_W / 2, SV_W / 2, 0, SV_H, c=1.5)
    horn = Cyl(HORN_D / 2, HORN_T).move(0, 0, SV_H + HORN_T / 2)
    return body, horn


def mg90s(inverted=False):
    x0 = MS_SHAFT_X - MS_L
    body = P.bx(x0, MS_SHAFT_X, -MS_W / 2, MS_W / 2, 0, MS_H, c=0.8)
    ears = P.bx(x0 - 4.85, MS_SHAFT_X + 4.85, -MS_W / 2, MS_W / 2, MS_EAR_Z - 2.5, MS_EAR_Z)
    s = body + ears
    if inverted:
        s = s.mirror(0, 0, 1)
    return s


def hcsr04():
    pcb = P.bx(-1.6, 0, -22.5, 22.5, -10, 10)
    cans = U(CylX(8, 12).move(6, 13, 0), CylX(8, 12).move(6, -13, 0))
    return pcb, cans


def estop():
    base = Cyl(20, 4).move(0, 0, 2)
    collar = Cyl(14, 14).move(0, 0, 11)
    head = Cyl(20, 8, ).move(0, 0, 22)
    return base, collar, head


def spring_between(a, b, r=4.0):
    a, b = np.asarray(a, float), np.asarray(b, float)
    v = b - a
    L = np.linalg.norm(v)
    ay = np.degrees(np.arctan2(np.hypot(v[0], v[1]), v[2]))
    az = np.degrees(np.arctan2(v[1], v[0]))
    coil = U(*[Cyl(r, 1.0).move(0, 0, -L / 2 + 5 + i * (L - 10) / 18) for i in range(19)],
             Cyl(0.8, L))
    return coil.rot(0, ay, az).move(*((a + b) / 2))


# ---------------- pose e montagem
DEFAULT_POSE = dict(yaw=28.0, shoulder=38.0, elbow=-82.0, wrist=-36.0, curl1=18.0, curl2=22.0,
                    spring=(0, 2))   # indices dos furos SPRING_A / SPRING_B


def frames(pose):
    """Matrizes 4x4 de cada referencial no mundo."""
    def T(x=0, y=0, z=0):
        m = np.eye(4); m[:3, 3] = (x, y, z); return m

    def R(a):
        m = np.eye(4); m[:3, :3] = _rot_matrix(a); return m

    Zt = 2 * ACRYLIC + SHELL_Z + LS_T
    f = {}
    f["turret"] = T(0, 0, Zt) @ R((0, 0, pose["yaw"]))
    f["shoulder"] = f["turret"] @ T(SHOULDER_X, 0, SHOULDER_Z)
    f["upper"] = f["shoulder"] @ R((0, -pose["shoulder"], 0))
    f["elbow"] = f["upper"] @ T(L1)
    f["fore"] = f["elbow"] @ R((0, -pose["elbow"], 0))
    f["wrist"] = f["fore"] @ T(L2)
    f["hand"] = f["wrist"] @ R((0, -pose["wrist"], 0))
    return f


class Placed(Node):
    """No com matriz 4x4 (para previa). No OpenSCAD vira multmatrix."""

    def __init__(self, child, m):
        self.child, self.m = child, np.asarray(m, float)
        self.r, self.t = self.m[:3, :3], self.m[:3, 3]

    def aabb(self):
        lo, hi = self.child.aabb()
        c = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
        w = c @ self.r.T + self.t
        return w.min(0), w.max(0)

    def sdf(self, p):
        return self.child.sdf((p - self.t) @ self.r)

    def scad(self, ind=""):
        rows = ", ".join("[" + ", ".join(f"{v:.5g}" for v in row) + "]" for row in self.m)
        return f"{ind}multmatrix([{rows}])\n" + self.child.scad(ind + "  ")


def T4(x=0, y=0, z=0, rot=(0, 0, 0)):
    m = np.eye(4)
    m[:3, :3] = _rot_matrix(rot)
    m[:3, 3] = (x, y, z)
    return m


def build(pose=None, hardware=True):
    """Lista de (nome, no posicionado, cor, impresso?)."""
    pose = dict(DEFAULT_POSE, **(pose or {}))
    f = frames(pose)
    items = []
    grp = ["base"]

    def add(name, node, m, color, printed=True):
        items.append((name, Placed(node, m), color, printed, grp[0], m))

    add("base_plate", Ref("base_plate"), T4(), BLACK)
    add("base_shell", Ref("base_shell"), T4(z=ACRYLIC), BLACK)
    add("base_lid", Ref("base_lid"), T4(z=ACRYLIC + SHELL_Z), ORANGE_ACR)
    grp[0] = "turret"
    add("turret", Ref("turret"), f["turret"], BLACK)
    for sy in (1, -1):   # v0.2: ombro com 2 servos lado a lado
        add("servo_cap", Ref("servo_cap"), f["shoulder"] @ T4(y=sy * SH_OFF), BLACK)
    xr_ = SHOULDER_X + P.PX0
    add("presilha_cabo", Ref("presilha_cabo"), f["turret"] @ T4(xr_ + (TCLIP_X[0] + TCLIP_X[1]) / 2, TCLIP_Y[0] + CLIP_ABA / 2 + 1.0,
                                                            TCLIP_Z0 + TCLIP_H), BLACK)
    grp[0] = "upper"
    add("upper_arm", Ref("upper_arm"), f["upper"], BLACK)
    add("upper_cover", Ref("upper_cover"), f["upper"], BLACK)
    yarm = POCKET_Y - 0.8 + 1.0
    add("upper_armor", Ref("upper_armor"), f["upper"] @ T4(y=-yarm), ORANGE)
    add("upper_armor", Ref("upper_armor").mirror(0, 1, 0), f["upper"] @ T4(y=yarm), ORANGE)
    zc_ = -BEAM_H / 2 - 3
    for x_ in (BRIDGE_X1 + 3, L1 + P.XC):
        add("presilha_cabo", Ref("presilha_cabo"), f["upper"] @ T4(x_, 0, zc_, rot=(0, 180, 0)), BLACK)
    add("servo_cap", Ref("servo_cap"), f["elbow"], BLACK)
    grp[0] = "fore"
    add("forearm", Ref("forearm"), f["fore"], BLACK)
    add("fore_cover", Ref("fore_cover"), f["fore"], BLACK)
    add("fore_armor", Ref("fore_armor"), f["fore"] @ T4(y=-yarm), ORANGE)
    add("fore_armor", Ref("fore_armor").mirror(0, 1, 0), f["fore"] @ T4(y=yarm), ORANGE)
    for x_ in (BRIDGE_X1 + 3, L2 + P.XC):
        add("presilha_cabo", Ref("presilha_cabo"), f["fore"] @ T4(x_, 0, zc_, rot=(0, 180, 0)), BLACK)
    add("servo_cap", Ref("servo_cap"), f["wrist"], BLACK)
    grp[0] = "hand"
    add("palm", Ref("palm"), f["hand"], BLACK)
    add("palm_lid", Ref("palm_lid"), f["hand"], ORANGE)

    for fy, fz, thumb in FINGERS:
        base = f["hand"] @ T4(KNUCKLE_X, fy, fz, rot=(180, 0, 0) if thumb else (0, 0, 0))
        m1 = base @ T4(rot=(0, pose["curl1"], 0))
        m2 = m1 @ T4(PH1, rot=(0, pose["curl2"], 0))
        add("finger_proximal", Ref("finger_proximal"), m1, BLACK)
        add("finger_distal", Ref("finger_distal"), m2, BLACK)
        add("finger_pad", Ref("finger_pad"), m2 @ T4((8 + PH2 - 3) / 2, 0, -FT / 2 + 1.2, rot=(180, 0, 0)), TPU)

    floor = -PALM_Z + PALM_WALL
    for sx, sy, inv in P.FINGER_SERVOS:
        zs = (PALM_Z - 0.5) if inv else (floor + 0.5)
        if hardware:
            add("mg90s", mg90s(inv), f["hand"] @ T4(sx, sy, zs), SERVO, False)
        zsp = zs - MS_H - 4.5 - 4.2 if inv else zs + MS_H + 4.5 + 4.2     # eixo + horn ~4,5 mm (MEDIR)
        add("spool", Ref("spool"), f["hand"] @ T4(sx, sy, zsp), BLACK)

    grp[0] = "base"   # v0.2: sem mastro/webcam (a webcam vai num movel)

    if hardware:
        body, horns = sts3215_vertical()
        m = T4(0, 0, ACRYLIC + P.YAW_BOT, rot=(0, 0, 0))
        add("sts3215", body, m, SERVO, False)
        add("horn", horns, m, METAL, False)
        for key, g, ms in (("shoulder", "turret", [(T4(y=SH_OFF), 1), (T4(y=-SH_OFF), -1)]),
                           ("elbow", "upper", [(T4(), 0)]), ("wrist", "fore", [(T4(), 0)])):
            grp[0] = g
            for mm, side in ms:
                body, horns = sts3215(side)
                add("sts3215", body, f[key] @ mm, SERVO, False)
                add("horn", horns, f[key] @ mm, METAL, False)
        grp[0] = "hand"
        pcb, cans = hcsr04()
        sm = f["hand"] @ T4(PALM_X1 - 6.5, 0, PALM_Z + 2.4 + 12.5)
        add("hcsr04", pcb, sm, PCB, False)
        add("hcsr04", cans, sm, METAL, False)
        grp[0] = "base"
        ls = P.bx(-LS_SIZE / 2, LS_SIZE / 2, -LS_SIZE / 2, LS_SIZE / 2, 0, LS_T, c=1) - Cyl(LS_HOLE / 2, 20)
        add("lazy_susan", ls, T4(z=ACRYLIC + SHELL_Z + ACRYLIC), METAL, False)
        b, c, h = estop()
        em = T4(P.ESTOP_XY[0], P.ESTOP_XY[1], 2 * ACRYLIC + SHELL_Z)
        add("estop", b, em, YELLOW, False)
        add("estop", c, em, (0.2, 0.2, 0.2), False)
        add("estop", h, em, RED, False)
    return items
