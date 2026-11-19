"""Auditoria de encaixe da eletronica na base do MK I (v0.2c), 19/11/2026.

Usa a carcaca real (parts.base_shell) e as medidas dos modulos que vamos COMPRAR
(fichas oficiais quando existem; 'estim.' = medida tipica, conferir com regua).
Confere: (1) modulo x carcaca, (2) modulo x modulo, (3) plugue USB-B do Arduino
x janela traseira, (4) profundidade do bloco do e-stop.

Rodar a partir da raiz da pasta MK1:
    python 03_docs/auditoria/eletronica_encaixe.py 04_imagens/eletronica_encaixe_v02c.png
"""
import sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "02_cad_fonte", "cad"))
import parts as P
from params import *

X, Y = SHELL_X / 2, SHELL_Y / 2
FLOOR = WALL                      # topo do fundo da carcaca
LID_UNDER = SHELL_Z               # face de baixo da tampa de acrilico
BOARD_Z = WALL + 6.0              # topo das colunas do UNO (Cyl(3.2,6) em z=WALL+3)
PCB = 1.6
# Arduino UNO R3 (desenho oficial): conector USB-B em y 31,75..43,82 da placa, sobra 6,35 mm
# para fora da borda x=0, altura 10,9 mm acima da placa.
USB_Y = (31.75, 43.82)
USB_OUT, USB_H = 6.35, 10.9
PLUG_W, PLUG_H, PLUG_L = 16.0, 11.5, 30.0   # capa do plugue USB-B (cabo do kit; estim.)

def boxes(spacer=0.0):
    bz = BOARD_Z + spacer
    ux0, uy0 = P.UNO_O
    ucy = uy0 + sum(USB_Y) / 2
    ucz = bz + PCB + USB_H / 2
    return {
        # nome: (x0, x1, y0, y1, z0, z1, rotulo, fonte)
        "arduino_uno": (ux0, ux0 + 68.6, uy0, uy0 + 53.4, bz, bz + PCB + 22, "Arduino UNO\n68,6x53,4 (+jumpers)", "oficial"),
        "plugue_usb_b": (ux0 - USB_OUT - PLUG_L, ux0 - USB_OUT, ucy - PLUG_W / 2, ucy + PLUG_W / 2,
                         ucz - PLUG_H / 2, ucz + PLUG_H / 2, "plugue USB-B", "estim."),
        "waveshare": (22, 64, 30, 63, FLOOR, FLOOR + 18.5, "Waveshare (A)\n42x33x18,5", "oficial"),
        "rele_modulo": (-62, -12, -70, -44, FLOOR, FLOOR + 19, "Rele 1 canal\n50x26x19", "estim."),
        "fusivel": (-62, -12, -64, -52, 30, 44, "porta-fusivel\n(sobre o rele)", "estim."),
        "wago_2x": (-58, -20.8, -34, -20.9, FLOOR, FLOOR + 8.2, "2x Wago 221-413", "oficial"),
        "jack_dc": (-X + WALL, -X + WALL + 22, -48, -32, 18, 34, "jack DC", "estim."),
        "estop_bloco": (P.ESTOP_XY[0] - 16.5, P.ESTOP_XY[0] + 16.5, P.ESTOP_XY[1] - 16.5, P.ESTOP_XY[1] + 16.5,
                        LID_UNDER - 48, LID_UNDER, "e-stop\n33x33x48", "estim."),
    }

def hit_shell(shell, b, step=1.0):
    x0, x1, y0, y1, z0, z1 = b[:6]
    g = np.mgrid[x0 + .3:x1 - .3:step, y0 + .3:y1 - .3:step, z0 + .3:z1 - .3:step].reshape(3, -1).T
    return float((shell.sdf(g) < -0.2).sum() * step ** 3)

def overlaps(B, skip=(("arduino_uno", "plugue_usb_b"),)):
    out, names = [], list(B)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if (names[i], names[j]) in skip:
                continue
            a, c = B[names[i]], B[names[j]]
            ov = [max(0, min(a[2 * k + 1], c[2 * k + 1]) - max(a[2 * k], c[2 * k])) for k in range(3)]
            if ov[0] * ov[1] * ov[2] > 0:
                out.append((names[i], names[j], round(ov[0] * ov[1] * ov[2])))
    return out

def window_ok(B, win):
    """win = (y0, y1, z0, z1) da janela do painel traseiro."""
    p = B["plugue_usb_b"]
    return dict(folga_y=(round(p[2] - win[0], 1), round(win[1] - p[3], 1)),
                folga_z=(round(p[4] - win[2], 1), round(win[3] - p[5], 1)))

def draw(path, B, win_now, win_new):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(14, 6.5), gridspec_kw=dict(width_ratios=[1.6, 1]))
    ax.add_patch(Rectangle((-X, -Y), SHELL_X, SHELL_Y, fc="#222", ec="k"))
    ax.add_patch(Rectangle((-X + WALL, -Y + WALL), SHELL_X - 2 * WALL, SHELL_Y - 2 * WALL, fc="#f4f4f4", ec="k"))
    for (px, py) in P.lid_corners():
        ax.add_patch(Circle((px, py), 5.5, fc="#555"))
    ax.add_patch(Rectangle((POCKET_X0 - WALL, -SV_W / 2 - TOL - WALL), POCKET_X1 - POCKET_X0 + 2 * WALL,
                           SV_W + 2 * TOL + 2 * WALL, fc="#999", ec="k"))
    ax.text(-10, 0, "servo de giro", ha="center", va="center", fontsize=7)
    ax.add_patch(Circle((0, 0), 31, fill=False, ls="--", ec="#c50"))
    cols = {"arduino_uno": "#2a7", "plugue_usb_b": "#0a5", "waveshare": "#27c", "rele_modulo": "#a4c",
            "fusivel": "#e90", "wago_2x": "#777", "jack_dc": "#444", "estop_bloco": "#d22"}
    for n, b in B.items():
        ax.add_patch(Rectangle((b[0], b[2]), b[1] - b[0], b[3] - b[2], fc=cols[n],
                               alpha=0.45 if n == "fusivel" else 0.8, ec="k"))
        ax.text((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, b[6], ha="center", va="center", fontsize=6.5, color="w")
    ax.annotate("TRAS: jack 12 V + janela USB", (-X, 0), (-X - 5, -Y - 14), fontsize=8)
    ax.annotate("FRENTE", (X, 0), (X - 30, -Y - 14), fontsize=8)
    ax.set_xlim(-X - 45, X + 10); ax.set_ylim(-Y - 20, Y + 10); ax.set_aspect("equal")
    ax.set_title("Base vista de cima (sem tampa), mm - modulos a comprar")
    # vista do painel traseiro (olhando de fora): eixo horizontal = y, vertical = z
    bx.add_patch(Rectangle((-Y, 0), SHELL_Y, SHELL_Z, fc="#333", ec="k"))
    bx.add_patch(Rectangle((win_now[0], win_now[2]), win_now[1] - win_now[0], win_now[3] - win_now[2],
                           fc="#f4f4f4", ec="k", label="janela atual"))
    bx.add_patch(Rectangle((win_new[0], win_new[2]), win_new[1] - win_new[0], win_new[3] - win_new[2],
                           fill=False, ec="#c50", lw=2, ls="--", label="janela proposta"))
    p = B["plugue_usb_b"]
    bx.add_patch(Rectangle((p[2], p[4]), p[3] - p[2], p[5] - p[4], fc="#0a5", alpha=0.7, ec="k", label="plugue USB-B"))
    bx.add_patch(Circle((-40, 26), 6, fc="#f4f4f4", ec="k"))
    bx.text(-40, 36, "jack 12 V", ha="center", fontsize=7, color="w")
    bx.set_xlim(-Y - 5, Y + 5); bx.set_ylim(-5, SHELL_Z + 5); bx.set_aspect("equal")
    bx.legend(loc="lower left", fontsize=7); bx.set_title("Painel traseiro (y, z), mm")
    fig.tight_layout(); fig.savefig(path, dpi=130)

if __name__ == "__main__":
    shell = P.base_shell()
    WIN_NOW = (42, 66, 8, 34)         # parts.base_shell() desde 19/11 (antes 40, 62, 19, 33)
    WIN_NEW = (42, 66, 8, 34)         # proposta (precisa de OK: muda base_shell e o lote 4)
    B = boxes()
    print("== colisao modulo x carcaca (mm3; 0 = livre) ==")
    for n, b in B.items():
        if n == "plugue_usb_b":
            continue
        print(f"  {n:13s} {hit_shell(shell, b):8.0f}")
    print("== sobreposicao entre modulos ==", overlaps(B) or "nenhuma")
    print("== plugue USB-B x janela traseira (folga negativa = bate) ==")
    print("  janela atual   :", window_ok(B, WIN_NOW))
    print("  janela proposta:", window_ok(B, WIN_NEW))
    B10 = boxes(spacer=10.0)
    print("  janela atual + espacador 10 mm:", window_ok(B10, WIN_NOW))
    e = B["estop_bloco"]
    print(f"== e-stop: profundidade livre sob a tampa = {LID_UNDER - FLOOR:.1f} mm, bloco {e[5]-e[4]:.0f} mm, "
          f"sobra {e[4]-FLOOR:.1f} mm; parede y: {e[2] - (-Y + WALL):.1f} mm ==")
    draw(sys.argv[1] if len(sys.argv) > 1 else "eletronica_encaixe.png", B, WIN_NOW, WIN_NEW)
