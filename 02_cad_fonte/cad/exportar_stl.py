"""v0.2c: exporta STL exatos (mm) das pecas que mudaram com a correcao das paredes (18/11).
Usa manifold3d (pip install manifold3d trimesh) para fazer as booleanas, igual ao OpenSCAD.
Uso: python exportar_stl.py <pasta_saida>"""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assembly as A
from csg_manifold import to_trimesh
OUT = sys.argv[1]
PECAS = ["upper_arm", "forearm", "turret", "servo_cap", "upper_cover", "fore_cover", "base_shell"]
os.makedirs(OUT, exist_ok=True)
for name in PECAS:
    node = A.part(name)
    tm = to_trimesh(node)
    tm.export(os.path.join(OUT, name + ".stl"))
    err = np.abs(node.sdf(tm.vertices)).max()
    ext = tm.bounds[1] - tm.bounds[0]
    print(f"{name:12s} estanque={tm.is_watertight} volume={tm.volume/1000:6.1f} cm3 medidas={np.round(ext,1).tolist()} erro_max={err:.3f} mm", flush=True)
