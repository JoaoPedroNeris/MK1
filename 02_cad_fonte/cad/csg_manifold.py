"""Converte a arvore CSG (csg.py) em malha exata com manifold3d (mesmo resultado do OpenSCAD).
Uso: from csg_manifold import to_trimesh"""
import numpy as np, trimesh
import manifold3d as mf
import csg as C

FN = 96   # segmentos por circulo (furos de inserto ficam com erro < 0,01 mm)


def _xf(man, m3, t=(0, 0, 0)):
    M = np.zeros((3, 4)); M[:, :3] = m3; M[:, 3] = t
    return man.transform(M)


def conv(n):
    if isinstance(n, C.Box):
        sx, sy, sz = n.h * 2
        if n.c <= 0:
            return mf.Manifold.cube((sx, sy, sz), True)
        c2 = 2 * n.c
        cubes = [mf.Manifold.cube(v, True) for v in ((sx, sy - c2, sz - c2), (sx - c2, sy, sz - c2), (sx - c2, sy - c2, sz))]
        return mf.Manifold.batch_hull(cubes)
    if isinstance(n, C.Cyl):
        if n.fn:
            return conv(n._poly)
        return mf.Manifold.cylinder(n.hh * 2, n.r, n.r, FN, True)
    if isinstance(n, C.Prism):
        pts = n.pts
        area = 0.5 * np.sum(pts[:, 0] * np.roll(pts[:, 1], -1) - np.roll(pts[:, 0], -1) * pts[:, 1])
        if area < 0: pts = pts[::-1]
        cs = mf.CrossSection([pts.tolist()])
        return mf.Manifold.extrude(cs, n.hh * 2).translate((0, 0, -n.hh))
    if isinstance(n, C.Translate):
        return conv(n.child).translate(tuple(n.v))
    if isinstance(n, (C.Rotate, C.Mirror)):
        return _xf(conv(n.child), n.m)
    if isinstance(n, C.Color):
        return conv(n.child)
    if isinstance(n, C.Union):
        return mf.Manifold.batch_boolean([conv(k) for k in n.kids], mf.OpType.Add)
    if isinstance(n, C.Diff):
        a = conv(n.a)
        cuts = [conv(c) for c in n.cuts]
        return a - mf.Manifold.batch_boolean(cuts, mf.OpType.Add) if cuts else a
    if isinstance(n, C.Inter):
        out = conv(n.kids[0])
        for k in n.kids[1:]:
            out = out ^ conv(k)
        return out
    if hasattr(n, "node"):   # assembly.Ref
        return conv(n.node)
    raise TypeError(type(n))


def to_trimesh(node):
    m = conv(node).to_mesh()
    return trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts), process=True)
