"""
Mini CSG para o projeto MK I.

Uma unica arvore de geometria serve para tres coisas:
  1. gerar codigo OpenSCAD (.scad) para exportar STL/STEP;
  2. avaliar a geometria aqui mesmo (funcao de distancia com sinal), para
     calcular volume, massa, centro de massa e colisoes;
  3. renderizar imagens de previa.

Convencoes iguais as do OpenSCAD: milimetros, rotate([ax, ay, az]) aplica X,
depois Y, depois Z. Todas as primitivas nascem centradas na origem.
"""
import numpy as np

FN = 72  # resolucao de circulos no OpenSCAD


def _f(v):
    return f"{v:.4g}" if abs(v) >= 1e-9 else "0"


def _vec(v):
    return "[" + ", ".join(_f(x) for x in v) + "]"


def _rot_matrix(a):
    ax, ay, az = np.radians(a)
    cx, sx, cy, sy, cz, sz = np.cos(ax), np.sin(ax), np.cos(ay), np.sin(ay), np.cos(az), np.sin(az)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return rz @ ry @ rx


def _aabb_dist(p, lo, hi):
    q = np.maximum(np.maximum(lo - p, p - hi), 0.0)
    return np.sqrt((q * q).sum(axis=1))


class Node:
    color_name = None

    # --- composicao ---
    def __add__(self, o):
        return Union([self, o])

    def __sub__(self, o):
        return Diff(self, [o])

    def __and__(self, o):
        return Inter([self, o])

    def move(self, x=0, y=0, z=0):
        return Translate(self, (x, y, z))

    def rot(self, x=0, y=0, z=0):
        return Rotate(self, (x, y, z))

    def mirror(self, x=0, y=0, z=0):
        return Mirror(self, (x, y, z))

    def color(self, c):
        return Color(self, c)

    # --- avaliacao ---
    def aabb(self):
        raise NotImplementedError

    def sdf(self, p):
        raise NotImplementedError

    def scad(self, ind=""):
        raise NotImplementedError


def _indent(s, ind):
    return "\n".join(ind + line if line else line for line in s.split("\n"))


# ---------------------------------------------------------------- primitivas
class Box(Node):
    """Caixa centrada com chanfro opcional c em todas as arestas."""

    def __init__(self, sx, sy, sz, c=0.0):
        self.h = np.array([sx, sy, sz], float) / 2
        self.c = float(min(c, *(self.h * 0.99)))

    def aabb(self):
        return -self.h.copy(), self.h.copy()

    def sdf(self, p):
        a = np.abs(p)
        q = a - self.h
        d = np.sqrt((np.maximum(q, 0) ** 2).sum(1)) + np.minimum(q.max(1), 0)
        if self.c > 0:
            hx, hy, hz = self.h
            c = self.c
            s2, s3 = np.sqrt(2), np.sqrt(3)
            d = np.maximum(d, (a[:, 0] + a[:, 1] - (hx + hy - c)) / s2)
            d = np.maximum(d, (a[:, 1] + a[:, 2] - (hy + hz - c)) / s2)
            d = np.maximum(d, (a[:, 0] + a[:, 2] - (hx + hz - c)) / s2)
            d = np.maximum(d, (a.sum(1) - (hx + hy + hz - 2 * c)) / s3)
        return d

    def scad(self, ind=""):
        sx, sy, sz = self.h * 2
        if self.c <= 0:
            return f"{ind}cube({_vec((sx, sy, sz))}, center=true);"
        c2 = 2 * self.c
        return (f"{ind}hull() {{\n"
                f"{ind}  cube({_vec((sx, sy - c2, sz - c2))}, center=true);\n"
                f"{ind}  cube({_vec((sx - c2, sy, sz - c2))}, center=true);\n"
                f"{ind}  cube({_vec((sx - c2, sy - c2, sz))}, center=true);\n"
                f"{ind}}}")


class Cyl(Node):
    """Cilindro centrado, eixo Z. fn=6 gera prisma hexagonal (cabecas de parafuso)."""

    def __init__(self, r, h, fn=None):
        self.r, self.hh, self.fn = float(r), float(h) / 2, fn
        if fn:
            ang = np.radians(np.arange(fn) * 360.0 / fn)
            self._poly = Prism(np.c_[r * np.cos(ang), r * np.sin(ang)], h)

    def aabb(self):
        return np.array([-self.r, -self.r, -self.hh]), np.array([self.r, self.r, self.hh])

    def sdf(self, p):
        if self.fn:
            return self._poly.sdf(p)
        dx = np.sqrt(p[:, 0] ** 2 + p[:, 1] ** 2) - self.r
        dz = np.abs(p[:, 2]) - self.hh
        return np.minimum(np.maximum(dx, dz), 0) + np.sqrt(np.maximum(dx, 0) ** 2 + np.maximum(dz, 0) ** 2)

    def scad(self, ind=""):
        fn = self.fn or FN
        return f"{ind}cylinder(r={_f(self.r)}, h={_f(self.hh * 2)}, center=true, $fn={fn});"


def CylX(r, h, fn=None):
    return Cyl(r, h, fn).rot(0, 90, 0)


def CylY(r, h, fn=None):
    return Cyl(r, h, fn).rot(90, 0, 0)


class Prism(Node):
    """Poligono 2D no plano XY extrudado em Z, centrado."""

    def __init__(self, pts, h):
        self.pts = np.asarray(pts, float)
        self.hh = float(h) / 2

    def aabb(self):
        lo = self.pts.min(0)
        hi = self.pts.max(0)
        return np.array([lo[0], lo[1], -self.hh]), np.array([hi[0], hi[1], self.hh])

    def sdf2(self, q):
        v = self.pts
        n = len(v)
        d = ((q - v[0]) ** 2).sum(1)
        s = np.ones(len(q))
        for i in range(n):
            a, b = v[i], v[i - 1]
            e = b - a
            w = q - a
            t = np.clip((w @ e) / (e @ e), 0, 1)
            bb = w - np.outer(t, e)
            d = np.minimum(d, (bb ** 2).sum(1))
            c1 = q[:, 1] >= a[1]
            c2 = q[:, 1] < b[1]
            c3 = e[0] * w[:, 1] > e[1] * w[:, 0]
            flip = (c1 & c2 & c3) | (~c1 & ~c2 & ~c3)
            s = np.where(flip, -s, s)
        return s * np.sqrt(d)

    def sdf(self, p):
        dx = self.sdf2(p[:, :2])
        dz = np.abs(p[:, 2]) - self.hh
        return np.minimum(np.maximum(dx, dz), 0) + np.sqrt(np.maximum(dx, 0) ** 2 + np.maximum(dz, 0) ** 2)

    def scad(self, ind=""):
        pts = ", ".join(_vec(q) for q in self.pts)
        return f"{ind}linear_extrude(height={_f(self.hh * 2)}, center=true) polygon([{pts}]);"


def stadium(length, width, n=12):
    """Pontos 2D de um rasgo (oblongo) centrado, comprido em X."""
    r = width / 2
    a = length / 2 - r
    pts = []
    for t in np.linspace(-90, 90, n):
        pts.append((a + r * np.cos(np.radians(t)), r * np.sin(np.radians(t))))
    for t in np.linspace(90, 270, n):
        pts.append((-a + r * np.cos(np.radians(t)), r * np.sin(np.radians(t))))
    return np.array(pts)


def chamfer_rect(w, h, c):
    x, y = w / 2, h / 2
    return np.array([(-x + c, -y), (x - c, -y), (x, -y + c), (x, y - c),
                     (x - c, y), (-x + c, y), (-x, y - c), (-x, -y + c)])


# ---------------------------------------------------------------- transformacoes
def _xform_aabb(lo, hi, m, t):
    corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    w = corners @ m.T + np.asarray(t, float)
    return w.min(0), w.max(0)


class Translate(Node):
    def __init__(self, child, v):
        self.child, self.v = child, np.asarray(v, float)

    def aabb(self):
        lo, hi = self.child.aabb()
        return lo + self.v, hi + self.v

    def sdf(self, p):
        return self.child.sdf(p - self.v)

    def scad(self, ind=""):
        return f"{ind}translate({_vec(self.v)})\n" + self.child.scad(ind + "  ")


class Rotate(Node):
    def __init__(self, child, a):
        self.child, self.a = child, tuple(a)
        self.m = _rot_matrix(a)

    def aabb(self):
        lo, hi = self.child.aabb()
        return _xform_aabb(lo, hi, self.m, (0, 0, 0))

    def sdf(self, p):
        return self.child.sdf(p @ self.m)

    def scad(self, ind=""):
        return f"{ind}rotate({_vec(self.a)})\n" + self.child.scad(ind + "  ")


class Mirror(Node):
    def __init__(self, child, n):
        n = np.asarray(n, float)
        self.n = n / np.linalg.norm(n)
        self.m = np.eye(3) - 2 * np.outer(self.n, self.n)
        self.child = child

    def aabb(self):
        lo, hi = self.child.aabb()
        return _xform_aabb(lo, hi, self.m, (0, 0, 0))

    def sdf(self, p):
        return self.child.sdf(p @ self.m)

    def scad(self, ind=""):
        return f"{ind}mirror({_vec(self.n)})\n" + self.child.scad(ind + "  ")


class Color(Node):
    def __init__(self, child, c):
        self.child, self.c = child, c

    def aabb(self):
        return self.child.aabb()

    def sdf(self, p):
        return self.child.sdf(p)

    def scad(self, ind=""):
        c = f'"{self.c}"' if isinstance(self.c, str) else _vec(self.c)
        return f"{ind}color({c})\n" + self.child.scad(ind + "  ")


# ---------------------------------------------------------------- booleanas
class Union(Node):
    def __init__(self, kids):
        flat = []
        for k in kids:
            flat.extend(k.kids if isinstance(k, Union) else [k])
        self.kids = flat
        self._bb = [k.aabb() for k in flat]

    def aabb(self):
        return np.min([b[0] for b in self._bb], 0), np.max([b[1] for b in self._bb], 0)

    def sdf(self, p):
        d = np.full(len(p), 1e9)
        for k, (lo, hi) in zip(self.kids, self._bb):
            db = _aabb_dist(p, lo - 0.01, hi + 0.01)
            m = db < d
            if m.any():
                d[m] = np.minimum(d[m], k.sdf(p[m]))
        return d

    def scad(self, ind=""):
        return f"{ind}union() {{\n" + "\n".join(k.scad(ind + "  ") for k in self.kids) + f"\n{ind}}}"


class Diff(Node):
    def __init__(self, a, cuts):
        if isinstance(a, Diff):  # achata diferencas encadeadas
            cuts = a.cuts + list(cuts)
            a = a.a
        self.a, self.cuts = a, list(cuts)
        self._bb = [c.aabb() for c in self.cuts]

    def __sub__(self, o):
        return Diff(self.a, self.cuts + [o])

    def aabb(self):
        return self.a.aabb()

    def sdf(self, p):
        d = self.a.sdf(p)
        for c, (lo, hi) in zip(self.cuts, self._bb):
            db = _aabb_dist(p, lo - 0.01, hi + 0.01)
            m = db <= np.maximum(-d, 0) + 1e-6
            if m.any():
                d[m] = np.maximum(d[m], -c.sdf(p[m]))
        return d

    def scad(self, ind=""):
        body = [self.a.scad(ind + "  ")] + [c.scad(ind + "  ") for c in self.cuts]
        return f"{ind}difference() {{\n" + "\n".join(body) + f"\n{ind}}}"


class Inter(Node):
    def __init__(self, kids):
        self.kids = kids

    def aabb(self):
        bbs = [k.aabb() for k in self.kids]
        return np.max([b[0] for b in bbs], 0), np.min([b[1] for b in bbs], 0)

    def sdf(self, p):
        return np.max([k.sdf(p) for k in self.kids], 0)

    def scad(self, ind=""):
        return f"{ind}intersection() {{\n" + "\n".join(k.scad(ind + "  ") for k in self.kids) + f"\n{ind}}}"


def U(*kids):
    return Union(list(kids))


# ---------------------------------------------------------------- analise
def mass_props(node, n=400_000, seed=1):
    """Volume (cm3) e centro de volume (mm) por Monte Carlo."""
    lo, hi = node.aabb()
    rng = np.random.default_rng(seed)
    p = lo + rng.random((n, 3)) * (hi - lo)
    inside = node.sdf(p) < 0
    vol = np.prod(hi - lo) * inside.mean() / 1000.0
    cg = p[inside].mean(0) if inside.any() else (lo + hi) / 2
    return vol, cg


def sample_inside(node, n=120_000, seed=2):
    lo, hi = node.aabb()
    rng = np.random.default_rng(seed)
    p = lo + rng.random((n, 3)) * (hi - lo)
    return p[node.sdf(p) < 0]
