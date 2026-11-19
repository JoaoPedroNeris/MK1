"""
Gera os arquivos de corte a laser da v0.2 (tampa e placa de base, acrilico 6 mm).

Uso: python exportar_laser.py <pasta_saida>
  -> <pasta>/base_lid_laranja_6mm.svg / .dxf
  -> <pasta>/base_plate_preta_6mm.svg / .dxf

SVG: vermelho = cortar, preto = gravar (texto e marcas dos grampos). Unidades em mm.
DXF (precisa de `pip install ezdxf`): camada CORTAR e camada GRAVAR, unidades em mm.
A geometria vem de parts.lid_2d() e parts.plate_2d(), a mesma que gera as malhas 3D.
"""
import os
import sys
import numpy as np
import parts as P
import build

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "out", "laser")
os.makedirs(OUT, exist_ok=True)

PECAS = [
    (P.lid_2d, "base_lid_laranja_6mm", "MK I v0.2 tampa da base - acrilico laranja 6 mm"),
    (P.plate_2d, "base_plate_preta_6mm", "MK I v0.2 placa de base - acrilico preto 6 mm"),
]


def dxf(d2, path):
    try:
        import ezdxf
    except ImportError:
        print("  ezdxf nao instalado: DXF pulado (pip install ezdxf)")
        return
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    doc.layers.add("CORTAR", color=1)
    doc.layers.add("GRAVAR", color=7)
    msp = doc.modelspace()
    cut = {"layer": "CORTAR"}
    msp.add_lwpolyline([tuple(p) for p in d2["outline"]], close=True, dxfattribs=cut)
    for x, y, dia in d2["holes"]:
        msp.add_circle((x, y), dia / 2, dxfattribs=cut)
    for x, y, ln, wd, a in d2["slots"]:
        st = P.stadium(ln, wd, n=24)
        ca, sa = np.cos(np.radians(a)), np.sin(np.radians(a))
        q = [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in st]
        msp.add_lwpolyline(q, close=True, dxfattribs=cut)
    for x, y, mw, mh in d2.get("marks", []):
        msp.add_lwpolyline([(x - mw / 2, y - mh / 2), (x + mw / 2, y - mh / 2),
                            (x + mw / 2, y + mh / 2), (x - mw / 2, y + mh / 2)],
                           close=True, dxfattribs={"layer": "GRAVAR"})
    for txt, x, y, size in d2.get("text", []):
        t = msp.add_text(txt, height=size * 0.7, dxfattribs={"layer": "GRAVAR"})
        t.set_placement((x, y), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    doc.saveas(path)


for fn, nome, titulo in PECAS:
    d2 = fn()
    build.svg(d2, os.path.join(OUT, nome + ".svg"), titulo)
    dxf(d2, os.path.join(OUT, nome + ".dxf"))
    lo, hi = np.min(d2["outline"], 0), np.max(d2["outline"], 0)
    print(f"{nome}: {hi[0] - lo[0]:.1f} x {hi[1] - lo[1]:.1f} mm, {len(d2['holes'])} furos, "
          f"{len(d2['slots'])} rasgos")
