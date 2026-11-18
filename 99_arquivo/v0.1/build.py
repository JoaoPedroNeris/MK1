"""
Gera tudo o que vai para fabricacao:
  out/scad/<peca>.scad   um arquivo OpenSCAD por peca (F6 e Exportar STL)
  out/scad/assembly.scad montagem colorida para conferir (F5)
  out/laser/*.svg        chapas de corte a laser (vermelho = cortar, preto = gravar)
  out/parts.csv          massa, volume e medidas de cada peca

Uso: python build.py
"""
import csv
import os
import numpy as np
import assembly as A
import parts as P
from csg import mass_props, FN

OUT = os.path.join(os.path.dirname(__file__), "out")
BED = (220.0, 220.0, 250.0)  # mesa de impressao conservadora; ajuste para a da universidade


def export_scad():
    d = os.path.join(OUT, "scad")
    os.makedirs(d, exist_ok=True)
    for name, (fn, qty, proc, mat, rho, fill, color) in A.PARTS.items():
        body = A.part(name).scad("  ")
        with open(os.path.join(d, f"{name}.scad"), "w") as fh:
            fh.write(f"// MK I - {name}\n// {proc} | {mat} | imprimir {qty}\n"
                     f"// Gerado por cad/build.py a partir de cad/parts.py: edite la, nao aqui.\n"
                     f"$fn = {FN};\n\nmodule {name}() {{\n{body}\n}}\n\n{name}();\n")
    items = A.build()
    with open(os.path.join(d, "assembly.scad"), "w") as fh:
        fh.write("// MK I - montagem completa (pose de exemplo). Abra no OpenSCAD e aperte F5.\n")
        fh.write(f"$fn = {FN};\n")
        for name in A.PARTS:
            fh.write(f"use <{name}.scad>\n")
        fh.write("\n")
        for name, node, color, printed, grp, m in items:
            c = "[" + ", ".join(f"{v:.3f}" for v in color) + "]"
            fh.write(f"// {name}\ncolor({c})\n{node.scad('  ')}\n")
    return d


def svg(d2, path, title):
    lo = np.min(d2["outline"], 0) - 5
    hi = np.max(d2["outline"], 0) + 5
    w, h = hi - lo

    def tx(x, y):
        return x - lo[0], hi[1] - y

    cut = 'fill="none" stroke="#ff0000" stroke-width="0.1"'
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.2f}mm" height="{h:.2f}mm" '
           f'viewBox="0 0 {w:.2f} {h:.2f}">', f"<title>{title}</title>"]
    pts = " ".join("%.3f,%.3f" % tx(*p) for p in d2["outline"])
    out.append(f'<polygon points="{pts}" {cut}/>')
    for x, y, dia in d2["holes"]:
        cx, cy = tx(x, y)
        out.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{dia / 2:.3f}" {cut}/>')
    for x, y, ln, wd, a in d2["slots"]:
        st = P.stadium(ln, wd, n=24)
        ca, sa = np.cos(np.radians(a)), np.sin(np.radians(a))
        q = [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in st]
        out.append(f'<polygon points="{" ".join("%.3f,%.3f" % tx(*p) for p in q)}" {cut}/>')
    for x, y, mw, mh in d2.get("marks", []):
        cx, cy = tx(x - mw / 2, y + mh / 2)
        out.append(f'<rect x="{cx:.3f}" y="{cy:.3f}" width="{mw}" height="{mh}" fill="none" '
                   f'stroke="#000000" stroke-width="0.6"/>')
    for txt, x, y, size in d2.get("text", []):
        cx, cy = tx(x, y)
        out.append(f'<text x="{cx:.3f}" y="{cy + size / 3:.3f}" font-family="Arial, Helvetica, sans-serif" '
                   f'font-weight="bold" font-size="{size}" text-anchor="middle" fill="#000000">{txt}</text>')
    out.append("</svg>")
    with open(path, "w") as fh:
        fh.write("\n".join(out))


def export_laser():
    d = os.path.join(OUT, "laser")
    os.makedirs(d, exist_ok=True)
    svg(P.lid_2d(), os.path.join(d, "base_lid_laranja_6mm.svg"), "MK I tampa da base - acrilico laranja 1/4 pol")
    svg(P.plate_2d(), os.path.join(d, "base_plate_preta_6mm.svg"), "MK I placa de base - acrilico preto 1/4 pol")
    return d


def fits_bed(dims):
    a, b, c = sorted(dims, reverse=True)
    if a <= BED[0] and b <= BED[1] and c <= BED[2]:
        return "sim"
    if np.hypot(BED[0], BED[1]) - 10 >= a and b <= 60 and c <= BED[2]:
        return "na diagonal"
    return "NAO"


def mass_table():
    rows = []
    for name, (fn, qty, proc, mat, rho, fill, color) in A.PARTS.items():
        nd = A.part(name)
        vol, cg = mass_props(nd, n=300_000)
        lo, hi = nd.aabb()
        dims = hi - lo
        m = vol * rho * fill
        rows.append(dict(peca=name, qtd=qty, processo=proc, material=mat,
                         medidas_mm="x".join(f"{v:.0f}" for v in dims),
                         volume_cm3=round(vol, 1), massa_g=round(m, 1),
                         cabe_na_mesa=fits_bed(dims) if proc != "Corte a laser" else "laser"))
    with open(os.path.join(OUT, "parts.csv"), "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    return rows


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("scad ->", export_scad())
    print("laser ->", export_laser())
    for r in mass_table():
        print(f"{r['peca']:16s} x{r['qtd']}  {r['medidas_mm']:>14s}  {r['massa_g']:7.1f} g  {r['cabe_na_mesa']}")
