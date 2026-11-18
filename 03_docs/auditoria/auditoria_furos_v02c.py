"""Auditoria de paredes em volta de furos M3 (insertos, passantes, pilotos).
Mede, para cada furo: parede radial minima (em todas as direcoes e alturas), material no fundo
e se o furo esta realmente aberto (existe) na peca."""
import sys, json, numpy as np
import parts as P
from params import *

STEP = 0.05
RMAX = 15.0


def frame(axis):
    a = np.asarray(axis, float); a /= np.linalg.norm(a)
    t = np.array([1.0, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(a, t); u /= np.linalg.norm(u)
    v = np.cross(a, u)
    return a, u, v


def measure(inside, mouth, axis, r, depth, through=False, n_ang=72):
    """inside(pts)->bool. mouth: centro da boca do furo; axis: sentido de furacao."""
    a, u, v = frame(axis)
    mouth = np.asarray(mouth, float)
    hs = np.arange(1.2, depth - 0.2, 0.5) if depth > 1.8 else np.array([depth / 2])
    angs = np.radians(np.arange(0, 360, 360 / n_ang))
    steps = np.arange(r + STEP, r + RMAX, STEP)
    # o furo existe? (centro e meio raio vazios)
    probe = [mouth + a * h for h in hs]
    probe += [mouth + a * h + 0.8 * r * (np.cos(t) * u + np.sin(t) * v) for h in hs for t in angs[::9]]
    probe = np.array(probe)
    filled = inside(probe).mean()
    # parede radial
    best = (1e9, None, None)
    walls = np.zeros((len(hs), len(angs)))
    for i, h in enumerate(hs):
        dirs = np.cos(angs)[:, None] * u + np.sin(angs)[:, None] * v       # (A,3)
        pts = mouth + a * h + dirs[:, None, :] * steps[None, :, None]       # (A,S,3)
        ins = inside(pts.reshape(-1, 3)).reshape(len(angs), len(steps))
        out2 = ~ins[:, :-1] & ~ins[:, 1:]            # 2 amostras seguidas fora (ignora faces coincidentes)
        first_out = np.where(out2.any(1), np.argmax(out2, axis=1), len(steps) - 1)
        w = steps[first_out] - r - STEP / 2
        walls[i] = w
        j = int(np.argmin(w))
        if w[j] < best[0]:
            best = (float(w[j]), float(h), float(np.degrees(angs[j])), (dirs[j]).round(2).tolist())
    per_h = walls.min(1)
    res = dict(furo_vazio=bool(filled < 0.2), parede_min=round(best[0], 2), parede_meio=round(float(np.median(per_h)), 2),
               na_profundidade=round(best[1], 1), direcao=best[3])
    # fundo
    if not through:
        bpts = [mouth + a * depth]
        bpts += [mouth + a * depth + 0.9 * r * (np.cos(t) * u + np.sin(t) * v) for t in angs[::6]]
        bmin = 1e9
        for b in bpts:
            ss = np.arange(STEP, RMAX, STEP)
            ins = inside(b + a[None, :] * ss[:, None])
            k = np.argmax(~ins) if (~ins).any() else len(ss) - 1
            bmin = min(bmin, ss[k] - STEP / 2)
        res["fundo"] = round(float(bmin), 2)
    return res


def csg_inside(node):
    return lambda p: node.sdf(np.asarray(p, float)) < 1e-3


def holes_pocket(ox, oy, oz):
    xf, xb = P.XF, P.XB
    out = []
    for nm, (x, y) in [("tampa servo frente", (xf, 0.0)), ("tampa servo tras +Y", (xb, 12.0)), ("tampa servo tras -Y", (xb, -12.0))]:
        out.append(dict(nome=nm, tipo="inserto", mouth=(ox + x, oy + y, oz + POCKET_Z), axis=(0, 0, -1),
                        r=INSERT_M3 / 2, depth=9.0))
    return out


def holes_link(L, off):
    hs = holes_pocket(L, 0, 0)
    for nm, x in [("tampa de baixo (lado do garfo)", BRIDGE_X1 + 3), ("tampa de baixo (lado do bolso)", L + P.XC)]:
        hs.append(dict(nome=nm, tipo="inserto", mouth=(x, 0, -BEAM_H / 2), axis=(0, 0, 1), r=INSERT_M3 / 2, depth=INSERT_L + 0.8))
    for s in (1, -1):
        y0 = s * (off + CLV_IN)
        for a in (45, 135, 225, 315):
            x = HORN_PCD / 2 * np.cos(np.radians(a)); z = HORN_PCD / 2 * np.sin(np.radians(a))
            hs.append(dict(nome="horn garfo %s %d°" % ("+Y" if s > 0 else "-Y", a), tipo="passante", mouth=(x, y0, z),
                           axis=(0, s, 0), r=SCREW_M3 / 2, depth=CLV_T, through=True))
    return hs


def run_csg():
    T = {}
    L = {"upper_arm (braço)": (P.upper_arm(), holes_link(L1, SH_OFF)),
         "forearm (antebraço)": (P.forearm(), holes_link(L2, 0.0))}
    # torre
    th = []
    for s in (1, -1):
        for h in holes_pocket(SHOULDER_X, s * SH_OFF, SHOULDER_Z):
            h["nome"] = h["nome"] + (" (servo +Y)" if s > 0 else " (servo -Y)")
            th.append(h)
    for a in (45, 135, 225, 315):
        x, y = HORN_PCD / 2 * np.cos(np.radians(a)), HORN_PCD / 2 * np.sin(np.radians(a))
        th.append(dict(nome="horn do giro %d° (autoatarr.)" % a, tipo="piloto", mouth=(x, y, -16 + 1.2), axis=(0, 0, 1),
                       r=PILOT_M3 / 2, depth=20 - 1.2 - 0.01))
    xr = SHOULDER_X + P.PX0
    xi, yi = xr + (TCLIP_X[0] + TCLIP_X[1]) / 2, TCLIP_Y[0] + CLIP_ABA / 2 + 1.0
    th.append(dict(nome="presilha do cabo (bloco)", tipo="inserto", mouth=(xi, yi, TCLIP_Z0 + TCLIP_H), axis=(0, 0, -1),
                   r=INSERT_M3 / 2, depth=INSERT_L + 0.8))
    L["turret (torre)"] = (P.turret(), th)
    # base
    bh = []
    for i, (px, py) in enumerate(P.lid_corners()):
        bh.append(dict(nome="coluna %d topo (tampa)" % (i + 1), tipo="inserto", mouth=(px, py, SHELL_Z), axis=(0, 0, -1),
                       r=INSERT_M3 / 2, depth=10))
        bh.append(dict(nome="coluna %d fundo (placa)" % (i + 1), tipo="inserto", mouth=(px, py, 0), axis=(0, 0, 1),
                       r=INSERT_M3 / 2, depth=8))
    for i, (hx, hy) in enumerate(P.UNO_HOLES):
        bh.append(dict(nome="suporte UNO %d (autoatarr.)" % (i + 1), tipo="piloto", mouth=(P.UNO_O[0] + hx, P.UNO_O[1] + hy, WALL + 6),
                       axis=(0, 0, -1), r=PILOT_M3 / 2, depth=7))
    L["base_shell (caixa da base)"] = (P.base_shell(), bh)
    # tampa do servo
    ch = []
    xf, xb = P.XF, P.XB
    for nm, (x, y) in [("frente", (xf, 0.0)), ("tras +Y", (xb, 12.0)), ("tras -Y", (xb, -12.0))]:
        ch.append(dict(nome="parafuso " + nm, tipo="passante", mouth=(x, y, P.PZ - 2.0), axis=(0, 0, -1), r=SCREW_M3 / 2,
                       depth=P.PZ - 2.0 - POCKET_Z, through=True))
        ch.append(dict(nome="rebaixo da cabeça " + nm, tipo="rebaixo", mouth=(x, y, P.PZ), axis=(0, 0, -1), r=3.2, depth=1.0, through=True))
    L["servo_cap (tampa do servo, x3)"] = (P.servo_cap(), ch)
    # tampas de baixo
    for nm, Lx in (("upper_cover", L1), ("fore_cover", L2)):
        hs = [dict(nome="parafuso %s" % k, tipo="passante", mouth=(x, 0, -BEAM_H / 2), axis=(0, 0, -1), r=SCREW_M3 / 2, depth=3, through=True)
              for k, x in (("garfo", BRIDGE_X1 + 3), ("bolso", Lx + P.XC))]
        L[nm + " (tampa de baixo)"] = (P.belly_cover(Lx), hs)
    L["presilha_cabo (x7)"] = (P.presilha_cabo(), [dict(nome="parafuso", tipo="passante", mouth=(0, 0, CABO_A + WALL), axis=(0, 0, -1),
                                                        r=SCREW_M3 / 2, depth=CABO_A + WALL, through=True)])
    for part, (node, hs) in L.items():
        ins = csg_inside(node)
        T[part] = []
        for h in hs:
            m = measure(ins, h["mouth"], h["axis"], h["r"], h["depth"], h.get("through", False))
            T[part].append(dict(nome=h["nome"], tipo=h["tipo"], **m))
    return T


if __name__ == "__main__":
    T = run_csg()
    json.dump(T, open(sys.argv[1] if len(sys.argv) > 1 else "auditoria_csg.json", "w"), indent=1, ensure_ascii=False)
    for p, rows in T.items():
        print("==", p)
        for r in rows:
            print("  %-42s %-9s vazio=%s parede=%.2f meio=%.2f fundo=%s dir=%s h=%s" % (r["nome"], r["tipo"], r["furo_vazio"], r["parede_min"], r["parede_meio"],
                                                                           r.get("fundo", "-"), r["direcao"], r["na_profundidade"]))
