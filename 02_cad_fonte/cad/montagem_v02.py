"""Gera malhas STL (mm) da montagem completa v0.2 na pose padrao, para ver no Fusion.
Bracos/base vem do CSG v0.2 (assembly.build); garra vem dos STLs do Fusion (v0.2/stl/garra)."""
import os, sys, json, numpy as np, trimesh
from skimage.measure import marching_cubes
sys.path.insert(0, os.path.dirname(__file__))
import assembly as A

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '05_visualizacao_fusion', 'montagem_b')
RES = float(sys.argv[2]) if len(sys.argv) > 2 else 0.6
SKIP = {'palm', 'palm_lid', 'finger_proximal', 'finger_distal', 'finger_pad', 'mg90s', 'spool', 'hcsr04', 'fit_coupon'}
os.makedirs(OUT, exist_ok=True)

def mesh_node(node, res):
    lo, hi = node.aabb(); lo = np.asarray(lo) - 2 * res; hi = np.asarray(hi) + 2 * res
    n = np.ceil((hi - lo) / res).astype(int) + 1
    xs = [np.linspace(lo[i], lo[i] + (n[i] - 1) * res, n[i]) for i in range(3)]
    vol = np.empty(n, np.float32)
    P = np.stack(np.meshgrid(xs[1], xs[2], indexing='ij'), -1).reshape(-1, 2)
    for i, x in enumerate(xs[0]):
        p = np.column_stack([np.full(len(P), x), P])
        vol[i] = node.sdf(p).reshape(n[1], n[2])
    v, f, _, _ = marching_cubes(vol, 0.0, spacing=(res, res, res))
    return trimesh.Trimesh(v + lo, f, process=True)

pose = dict(A.DEFAULT_POSE, shoulder=45.0)  # ombro 45 para a garra ficar acima da mesa
fr = A.frames(pose)
items = A.build(pose)
manifest, count = [], {}
for name, placed, color, printed, grp, m in items:
    if name in SKIP:
        continue
    count[name] = count.get(name, 0) + 1
    tag = name if count[name] == 1 else '%s_%d' % (name, count[name])
    child = placed.child
    res = RES if printed else max(RES, 1.0)
    try:
        tm = mesh_node(child, res)
    except Exception as e:
        print('FALHOU', tag, e); continue
    tm.apply_transform(m)
    fn = tag + '.stl'
    tm.export(os.path.join(OUT, fn))
    manifest.append(dict(file=fn, name=tag, color=list(color), printed=bool(printed), group=grp))
    print(tag, len(tm.faces), np.round(tm.bounds, 1).tolist(), flush=True)

# garra v0.2b: frame garra -> punho: X=z_g+71.5, Y=x_g, Z=y_g
G = np.array([[0, 0, 1, 71.5], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1.0]])
GD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '01_imprimir', '03_garra')
cols = {'garra_base': A.BLACK, 'carcaca': A.BLACK, 'disco_espiral': A.ORANGE, 'placa_guia': A.BLACK}
for fn in sorted(os.listdir(GD)):
    nm = fn[:-4]
    tm = trimesh.load(os.path.join(GD, fn))
    tm.apply_transform(fr['hand'] @ G)
    c = cols.get(nm, A.TPU if nm.startswith('ponta') else A.ORANGE)
    tm.export(os.path.join(OUT, 'garra_' + fn))
    manifest.append(dict(file='garra_' + fn, name='garra_' + nm, color=list(c), printed=True, group='garra'))
    print('garra_' + nm, np.round(tm.bounds, 1).tolist())
# eletronicos (caixas estimadas) dentro da base
import eletronica_v02 as E
ecol = {"arduino_uno": (0.1, 0.5, 0.35), "waveshare": (0.1, 0.3, 0.7), "rele": (0.5, 0.2, 0.6), "conversor": (0.7, 0.45, 0.1),
        "bornes": (0.5, 0.5, 0.5), "jack_dc": (0.2, 0.2, 0.2), "estop_bloco": (0.8, 0.1, 0.1)}
for n, b in E.BOX.items():
    if n not in ecol: continue
    x0, x1, y0, y1, z0, z1 = b[:6]
    tm = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    tm.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2 + A.ACRYLIC))
    fn = 'eletr_' + n + '.stl'; tm.export(os.path.join(OUT, fn))
    manifest.append(dict(file=fn, name='eletr_' + n, color=list(ecol[n]), printed=False, group='base'))
json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
print('total', len(manifest))
