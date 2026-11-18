"""
Renderizador de previa (sphere tracing sobre a mesma geometria do CAD).
Uso: python render.py  -> out/render_*.png
"""
import os
import time
import numpy as np
from PIL import Image
import assembly as A
from csg import _aabb_dist


def scene(items):
    objs = []
    for name, node, color, printed, grp, m in items:
        lo, hi = node.aabb()
        objs.append((node, np.array(color, float), lo - 0.5, hi + 0.5, name))
    return objs


def scene_sdf(objs, p, want_id=False):
    d = np.full(len(p), 1e9)
    ids = np.full(len(p), -1)
    for i, (node, col, lo, hi, name) in enumerate(objs):
        db = _aabb_dist(p, lo, hi)
        m = db < d
        if not m.any():
            continue
        di = node.sdf(p[m])
        better = di < d[m]
        idx = np.where(m)[0][better]
        d[idx] = di[better]
        ids[idx] = i
    return (d, ids) if want_id else d


def render(objs, eye, target, fov=35, size=(1280, 900), floor_z=0.0, out="render.png", spp_aa=1):
    W, H = size
    eye, target = np.array(eye, float), np.array(target, float)
    fwd = target - eye; fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 0, 1]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    tanf = np.tan(np.radians(fov) / 2)
    ys, xs = np.mgrid[0:H, 0:W]
    u = (2 * (xs + 0.5) / W - 1) * tanf * W / H
    v = (1 - 2 * (ys + 0.5) / H) * tanf
    dirs = fwd[None] + u.reshape(-1, 1) * right[None] + v.reshape(-1, 1) * up[None]
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    n = len(dirs)
    t = np.zeros(n)
    hit = np.zeros(n, bool)
    alive = np.ones(n, bool)
    # limite do raio: chao
    t_floor = np.where(dirs[:, 2] < -1e-6, (floor_z - eye[2]) / dirs[:, 2], 1e9)
    lo_all = np.min([o[2] for o in objs], 0); hi_all = np.max([o[3] for o in objs], 0)
    for step in range(260):
        idx = np.where(alive)[0]
        if len(idx) == 0:
            break
        p = eye + dirs[idx] * t[idx, None]
        d = scene_sdf(objs, p)
        eps = 0.04 + 0.0006 * t[idx]
        h = d < eps
        hit[idx[h]] = True
        alive[idx[h]] = False
        t[idx[~h]] += np.maximum(d[~h] * 0.9, 0.02)
        far = (t[idx] > t_floor[idx]) | (t[idx] > 3000)
        alive[idx[far & ~h]] = False
    # cores
    img = np.zeros((n, 3))
    sky_top, sky_bot = np.array([0.055, 0.06, 0.07]), np.array([0.16, 0.17, 0.19])
    img[:] = sky_bot + (sky_top - sky_bot) * np.clip(v.reshape(-1) / tanf * 0.5 + 0.5, 0, 1)[:, None]
    key = np.array([-0.45, -0.55, 0.70]); key /= np.linalg.norm(key)
    fill = np.array([0.7, 0.4, 0.35]); fill /= np.linalg.norm(fill)
    rim = np.array([0.2, 0.9, 0.25]); rim /= np.linalg.norm(rim)

    def shadow(P, L, maxt=900):
        s = np.ones(len(P)); tt = np.full(len(P), 1.5)
        for _ in range(70):
            q = P + L * tt[:, None]
            d = scene_sdf(objs, q)
            s = np.minimum(s, np.clip(10 * d / tt, 0, 1))
            tt += np.clip(d, 0.4, 25)
            if (tt > maxt).all():
                break
        return np.clip(s, 0, 1)

    # chao
    fl = (~hit) & (t_floor < 3000)
    if fl.any():
        P = eye + dirs[fl] * t_floor[fl, None]
        sh = shadow(P + np.array([0, 0, 0.2]), key)
        ao = np.clip(scene_sdf(objs, P + np.array([0, 0, 12.0])) / 12.0, 0.25, 1.0)
        base = np.array([0.20, 0.205, 0.215])
        r = np.hypot(P[:, 0] - 40, P[:, 1])
        vign = np.clip(1.15 - r / 900, 0.35, 1.0)
        img[fl] = base[None] * (0.35 + 0.65 * sh[:, None]) * ao[:, None] * vign[:, None]
    # objetos
    if hit.any():
        idx = np.where(hit)[0]
        P = eye + dirs[idx] * t[idx, None]
        _, ids = scene_sdf(objs, P, want_id=True)
        e = 0.08
        N = np.zeros_like(P)
        for i in np.unique(ids):
            mm = ids == i
            node = objs[i][0]
            q = P[mm]
            for k in range(3):
                dv = np.zeros(3); dv[k] = e
                N[mm, k] = node.sdf(q + dv) - node.sdf(q - dv)
        N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
        col = np.array([objs[i][1] for i in ids])
        V = -dirs[idx]
        sh = shadow(P + N * 0.6, key)
        ao = np.ones(len(P))
        for k, s in enumerate((1.5, 4.0, 9.0)):
            ao -= np.clip((s - scene_sdf(objs, P + N * s)) / s, 0, 1) * (0.22 / (k + 1))
        ao = np.clip(ao, 0.2, 1)
        dk = np.clip((N * key).sum(1), 0, 1) * sh
        df = np.clip((N * fill).sum(1), 0, 1)
        dr = np.clip((N * rim).sum(1), 0, 1)
        Hk = (key[None] + V); Hk /= np.linalg.norm(Hk, axis=1, keepdims=True)
        spec = np.clip((N * Hk).sum(1), 0, 1) ** 40 * sh
        fres = (1 - np.clip((N * V).sum(1), 0, 1)) ** 4
        lum = col.mean(1)
        shiny = np.where(lum < 0.2, 0.55, 0.30)
        c = col * (0.16 * ao[:, None] + 0.95 * dk[:, None] + 0.28 * df[:, None]) \
            + (spec * shiny)[:, None] + (0.10 * fres * ao)[:, None] * np.array([1.0, 0.75, 0.5]) \
            + (0.12 * dr * ao)[:, None] * np.array([0.6, 0.75, 1.0])
        img[idx] = c
    img = np.clip(img, 0, 1) ** (1 / 2.2)
    im = Image.fromarray((img.reshape(H, W, 3) * 255).astype(np.uint8))
    im.save(out)
    return out


if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)
    t0 = time.time()
    objs = scene(A.build())
    render(objs, eye=(620, -560, 470), target=(60, 20, 180), fov=36, size=(1400, 980),
           out="out/render_hero.png")
    print("hero", round(time.time() - t0, 1), "s")
