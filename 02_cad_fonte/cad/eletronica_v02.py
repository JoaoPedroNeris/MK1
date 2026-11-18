"""Confere se os eletronicos cabem dentro da carcaca da base (v0.2).
Medidas dos modulos sao ESTIMADAS (fichas tipicas); confira com regua quando chegarem.
Referencial: o da carcaca (z=0 no fundo da carcaca, tampa por baixo em z=SHELL_Z)."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import parts as P
from params import *

zin = WALL
# nome: (x0, x1, y0, y1, z0, z1, rotulo)
BOX = {
    "arduino_uno":   (P.UNO_O[0], P.UNO_O[0] + 68.6, P.UNO_O[1], P.UNO_O[1] + 53.4, 9.2, 24.0, "Arduino UNO 68,6x53,4"),
    "waveshare":     (22, 67, 30, 62, zin + 4, zin + 4 + 16, "Adaptador Waveshare ~45x32 (estim.)"),
    "rele":          (-62, -12, -70, -44, zin + 4, zin + 4 + 19, "Rele 1 canal ~50x26 (estim.)"),
    "conversor":     (-4, 39, -70, -49, zin + 4, zin + 4 + 14, "Conversor 12->5 V ~43x21 (estim.)"),
    "bornes":        (-60, -20, -36, -20, zin, zin + 18, "Bornes de alavanca 12 V (estim.)"),
    "jack_dc":       (-SHELL_X / 2 + WALL, -SHELL_X / 2 + WALL + 20, -48, -32, 18, 34, "Conector DC 12 V"),
    "estop_bloco":   (P.ESTOP_XY[0] - 16.5, P.ESTOP_XY[0] + 16.5, P.ESTOP_XY[1] - 16.5, P.ESTOP_XY[1] + 16.5, SHELL_Z - 45, SHELL_Z, "Bloco do e-stop ~33x33x45 (estim.)"),
    "servo_giro":    (POCKET_X0 - 2, POCKET_X1, -SV_W / 2, SV_W / 2, P.YAW_BOT, P.YAW_BOT + SV_H, "Servo de giro"),
}

def box_pts(b, step=1.5):
    x0, x1, y0, y1, z0, z1 = b[:6]
    g = np.mgrid[x0:x1:step, y0:y1:step, z0:z1:step].reshape(3, -1).T
    return g

def check():
    shell = P.base_shell()
    res = {}
    for n, b in BOX.items():
        if n == "servo_giro":
            continue
        pts = box_pts(b)
        hit = (shell.sdf(pts) < -0.2).sum() * 1.5 ** 3
        res[n] = round(float(hit))
    names = list(BOX)
    over = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, c = BOX[names[i]], BOX[names[j]]
            ov = [max(0, min(a[2 * k + 1], c[2 * k + 1]) - max(a[2 * k], c[2 * k])) for k in range(3)]
            v = ov[0] * ov[1] * ov[2]
            if v > 0:
                over.append((names[i], names[j], round(v)))
    return res, over

def draw(path):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    fig, ax = plt.subplots(figsize=(9, 8))
    X, Y = SHELL_X / 2, SHELL_Y / 2
    ax.add_patch(Rectangle((-X, -Y), SHELL_X, SHELL_Y, fc="#222", ec="k"))
    ax.add_patch(Rectangle((-X + WALL, -Y + WALL), SHELL_X - 2 * WALL, SHELL_Y - 2 * WALL, fc="#f4f4f4", ec="k"))
    for (px, py) in P.lid_corners():
        ax.add_patch(Circle((px, py), 5, fc="#555"))
    ax.add_patch(Rectangle((POCKET_X0 - WALL, -SV_W / 2 - TOL - WALL), POCKET_X1 - POCKET_X0 + 2 * WALL, SV_W + 2 * TOL + 2 * WALL, fc="#999", ec="k"))
    ax.add_patch(Circle((0, 0), 31, fill=False, ls="--", ec="#c50"))
    cols = {"arduino_uno": "#2a7", "waveshare": "#27c", "rele": "#a4c", "conversor": "#c82", "bornes": "#777",
            "jack_dc": "#444", "estop_bloco": "#d22", "servo_giro": "#333"}
    for n, b in BOX.items():
        ax.add_patch(Rectangle((b[0], b[2]), b[1] - b[0], b[3] - b[2], fc=cols[n], alpha=0.75, ec="k"))
        ax.text((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, b[6].replace(" ~", "\n~").replace(" (", "\n("), ha="center", va="center", fontsize=7, color="w")
    ax.text(0, -36, "cabos descem da torre aqui", ha="center", fontsize=7, color="#c50")
    ax.annotate("TRAS (painel: 12 V e USB)", (-X, 0), (-X - 4, -Y - 14), fontsize=8)
    ax.annotate("FRENTE", (X, 0), (X - 30, -Y - 14), fontsize=8)
    ax.set_xlim(-X - 10, X + 10); ax.set_ylim(-Y - 20, Y + 10); ax.set_aspect("equal")
    ax.set_title("MK I v0.2 - base vista de cima (sem tampa), mm")
    fig.tight_layout(); fig.savefig(path, dpi=130)

if __name__ == "__main__":
    r, o = check()
    print("colisao com a carcaca (mm3):", r)
    print("sobreposicao entre modulos (mm3):", o)
    draw(sys.argv[1] if len(sys.argv) > 1 else "eletronica_base.png")
