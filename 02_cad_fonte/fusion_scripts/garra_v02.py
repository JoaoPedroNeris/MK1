"""
MK I v0.2b - garra de 3 pontas a 120 graus, 1 STS3215, disco espiral (mandril).
Todos os parafusos sao M3.
Rode no Fusion (Utilitarios > Scripts e suplementos). Cria um documento novo.
Medidas em mm. Para mudar a geometria, edite PARAMS e rode de novo.

Referencial da garra: origem no centro do eixo do servo da garra, eixo da garra = +Z.
O punho (garfo que abraca o servo do punho) fica atras, com o eixo da junta
paralelo a X, em Z = -(BOX_DEPTH + BRIDGE_T + ...) (ver garra_base).
"""
import adsk.core, adsk.fusion, math

PARAMS = {
    # servo Feetech STS3215 (MEDIR)
    'SV_L': 45.2, 'SV_W': 24.7, 'SV_H': 35.0, 'SV_SHAFT_END': 11.0,
    'HORN_D': 22.0, 'HORN_T': 3.5, 'HORN_PCD': 14.0, 'HORN_CTR_D': 6.5,  # v0.2c: furo central do horn 9 -> 6,5 (parede 0,85 -> 2 mm)
    # fabricacao e parafusos (tudo M3)
    'TOL': 0.25, 'WALL': 3.2,
    'SCREW_M3': 3.4, 'INSERT_M3': 4.2, 'INSERT_DEPTH': 6.5, 'HEAD_M3': 5.5,
    # carcaca
    'case_D': 70.0, 'flange_hole_D': 24.0, 'case_top': 9.0,
    'ear_D': 11.0, 'ear_R': 37.5,
    # caixa do servo da garra (atras da flange)
    'box_end_wall': 10.6, 'box_back_gap': 0.5,
    'tab_x': -39.0,
    # garfo do punho (igual ao clevis da v0.1)
    'CLV_IN': 21.0, 'CLV_T': 5.0, 'CLV_R': 24.0, 'BRIDGE_T': 10.0, 'BEAM_H': 34.0,
    'joint_to_bridge': 26.0,
    # disco espiral
    'disc_D': 62.0, 'disc_T': 4.0, 'disc_center_hole': 6.0, 'horn_phase_deg': 35.0,
    'r_pin_min': 13.0, 'r_pin_max': 25.0, 'spiral_deg': 110.0,
    'pin_D': 3.0, 'slot_clear': 0.2,
    # placa-guia
    'plate_T': 6.0,
    # mordentes
    'jaw_half_L': 6.0, 'jaw_W': 8.0, 'jaw_flange_W': 12.0, 'jaw_flange_T': 3.2, 'blade_offset': 2.5,
    'blade_t': 3.2, 'blade_w': 6.0, 'blade_L': 40.0,
    'pad_t': 1.5, 'pad_L': 15.0,
    # v0.2b passa-cabos: inserto M3 na face de fora da caixa (lado +Y do punho) para a presilha do cabo
    'cabo_ins_y': -3.0, 'cabo_ins_z': -20.0,
}
JAW_ANGLES = (90.0, 210.0, 330.0)
EAR_ANGLES = (30.0, 150.0, 270.0)

app = adsk.core.Application.get()
NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation


def cm(v):
    return v / 10.0


def P3(x, y, z=0.0):
    return adsk.core.Point3D.create(cm(x), cm(y), cm(z))


def new_comp(root, name):
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ, occ.component


def extrude(c, profs, z0, h, op, name=None):
    ex = c.features.extrudeFeatures
    if not isinstance(profs, adsk.core.ObjectCollection):
        col = adsk.core.ObjectCollection.create()
        col.add(profs)
        profs = col
    inp = ex.createInput(profs, op)
    inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(cm(h))),
                         adsk.fusion.ExtentDirections.PositiveExtentDirection)
    inp.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(cm(z0)))
    if op == CUT:
        inp.participantBodies = [b for b in c.bRepBodies]   # corta so os corpos desta peca
    f = ex.add(inp)
    if name:
        f.name = name
        if f.bodies.count:
            f.bodies.item(0).name = name
    return f


class Sk:
    """Sketch que recebe pontos no referencial do modelo (mm)."""

    def __init__(self, c, plane):
        self.sk = c.sketches.add(plane)

    def p(self, x, y, z):
        return self.sk.modelToSketchSpace(P3(x, y, z))

    def poly(self, pts3):
        L = self.sk.sketchCurves.sketchLines
        q = [self.p(*t) for t in pts3]
        first = prev = None
        for i in range(1, len(q)):
            ln = L.addByTwoPoints(q[0] if prev is None else prev, q[i])
            if prev is None:
                first = ln.startSketchPoint
            prev = ln.endSketchPoint
        L.addByTwoPoints(prev, first)

    def circle(self, x, y, z, d):
        self.sk.sketchCurves.sketchCircles.addByCenterRadius(self.p(x, y, z), cm(d / 2))

    def profiles(self):
        col = adsk.core.ObjectCollection.create()
        for i in range(self.sk.profiles.count):
            col.add(self.sk.profiles.item(i))
        return col

    def outer_profile(self):
        best = None
        for i in range(self.sk.profiles.count):
            pr = self.sk.profiles.item(i)
            a = pr.areaProperties().area
            if best is None or a > best[0]:
                best = (a, pr)
        return best[1]


def ring_profile(sk):
    for i in range(sk.profiles.count):
        p = sk.profiles.item(i)
        if p.profileLoops.count == 2:
            return p
    raise RuntimeError('perfil de anel nao encontrado')


def uv(a_deg, u, v):
    a = math.radians(a_deg)
    return (u * math.cos(a) - v * math.sin(a), u * math.sin(a) + v * math.cos(a))


def rect_xy(c, x0, x1, y0, y1, z0, h, op, name=None):
    s = Sk(c, c.xYConstructionPlane)
    s.poly([(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)])
    return extrude(c, s.sk.profiles.item(0), z0, h, op, name)


def circ_xy(c, pts, d, z0, h, op, name=None):
    s = Sk(c, c.xYConstructionPlane)
    for (x, y) in pts:
        s.circle(x, y, 0, d)
    return extrude(c, s.profiles(), z0, h, op, name)


def build():
    p = PARAMS
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.name = 'MK1_garra_v02b'
    d = adsk.fusion.Design.cast(app.activeProduct)
    d.designType = adsk.fusion.DesignTypes.ParametricDesignType
    d.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    root = d.rootComponent
    for k, v in p.items():
        unit = 'deg' if k.endswith('_deg') else 'mm'
        d.userParameters.add(k, adsk.core.ValueInput.createByString('%g %s' % (v, unit)), unit, 'garra v0.2b')
    occs = {}
    R = p['case_D'] / 2
    T = p['TOL']
    W = p['WALL']

    # ---------- caixa do servo: cavidade, paredes, posicoes dos parafusos
    cx0 = -p['SV_SHAFT_END'] - T
    cx1 = p['SV_L'] - p['SV_SHAFT_END'] + T
    cy = p['SV_W'] / 2 + T
    bx0 = cx0 - W                    # parede da esquerda (lado curto, perto do eixo)
    bx1 = cx1 + p['box_end_wall']    # parede da direita, grossa para os insertos
    by = cy + W
    zc = -(p['SV_H'] + p['box_back_gap'])   # fundo da cavidade = face da ponte
    sx_r = cx1 + p['box_end_wall'] / 2
    FL_SCREWS = [(sx_r, 9.0), (sx_r, -9.0), (p['tab_x'], 0.0)]
    tab_x0 = p['tab_x'] - p['ear_D'] / 2 - 1.0

    # ---------- servo (referencia, nao imprime)
    o, c = new_comp(root, 'servo_STS3215')
    occs['servo'] = o
    rect_xy(c, -p['SV_SHAFT_END'], p['SV_L'] - p['SV_SHAFT_END'], -p['SV_W'] / 2, p['SV_W'] / 2, -p['SV_H'], p['SV_H'], NEW, 'corpo_servo')
    circ_xy(c, [(0, 0)], p['HORN_D'], 0, p['HORN_T'], NEW, 'horn')

    # ---------- garra_base: garfo do punho + ponte + caixa do servo (uma peca so)
    o, c = new_comp(root, 'garra_base')
    occs['garra_base'] = o
    zb1 = zc                              # face da frente da ponte
    zb0 = zb1 - p['BRIDGE_T']
    zj = zb1 - p['BRIDGE_T'] - p['joint_to_bridge'] + p['BRIDGE_T']  # eixo da junta do punho
    zj = zb1 - (p['joint_to_bridge'] + p['BRIDGE_T'])
    hb = p['BEAM_H'] / 2
    # caixa
    rect_xy(c, bx0, bx1, -by, by, zc, -zc, NEW, 'garra_base')
    # aba da esquerda para o 3o parafuso da flange
    rect_xy(c, tab_x0, bx0 + 0.5, -6.0, 6.0, -10.0, 10.0, JOIN)
    # ponte
    rect_xy(c, -(p['CLV_IN'] + p['CLV_T']), p['CLV_IN'] + p['CLV_T'], -hb, hb, zb0, p['BRIDGE_T'], JOIN)
    # placas do garfo (planos perpendiculares a X)
    for side in (1, -1):
        x_in = side * p['CLV_IN']
        x0 = min(x_in, x_in + side * p['CLV_T'])
        cpi = c.constructionPlanes.createInput()
        cpi.setByOffset(c.yZConstructionPlane, adsk.core.ValueInput.createByReal(cm(x0)))
        pl = c.constructionPlanes.add(cpi)
        s = Sk(c, pl)
        s.circle(x0, 0, zj, 2 * p['CLV_R'])
        s.poly([(x0, -hb, zj), (x0, -hb, zb1), (x0, hb, zb1), (x0, hb, zj)])
        ex = c.features.extrudeFeatures
        inp = ex.createInput(s.profiles(), JOIN)
        inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(cm(p['CLV_T']))),
                             adsk.fusion.ExtentDirections.PositiveExtentDirection)
        ex.add(inp)
        # furos do horn do servo do punho: centro + 4 M3
        s = Sk(c, pl)
        s.circle(x0, 0, zj, p['HORN_CTR_D'])
        for a in (45, 135, 225, 315):
            s.circle(x0, p['HORN_PCD'] / 2 * math.cos(math.radians(a)), zj + p['HORN_PCD'] / 2 * math.sin(math.radians(a)), p['SCREW_M3'])
        inp = ex.createInput(s.profiles(), CUT)
        inp.participantBodies = [b for b in c.bRepBodies]
        inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(cm(p['CLV_T'] + 2))),
                             adsk.fusion.ExtentDirections.PositiveExtentDirection)
        inp.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(cm(-1)))
        ex.add(inp)
    # cavidade do servo
    rect_xy(c, cx0, cx1, -cy, cy, zc, -zc + 1, CUT)
    # passagem do cabo pela ponte (igual a v0.1: 14 x 10)
    rect_xy(c, -7, 7, -5, 5, zb0 - 1, p['BRIDGE_T'] + 2, CUT)
    # insertos M3 da flange (furos de 6,5 mm a partir da face z=0)
    circ_xy(c, FL_SCREWS, p['INSERT_M3'], -p['INSERT_DEPTH'], p['INSERT_DEPTH'], CUT)
    # v0.2b: inserto M3 da presilha do cabo, horizontal, na face x = bx1 (parede grossa)
    cpi = c.constructionPlanes.createInput()
    cpi.setByOffset(c.yZConstructionPlane, adsk.core.ValueInput.createByReal(cm(bx1)))
    pl = c.constructionPlanes.add(cpi)
    s = Sk(c, pl)
    s.circle(bx1, p['cabo_ins_y'], p['cabo_ins_z'], p['INSERT_M3'])
    ex = c.features.extrudeFeatures
    inp = ex.createInput(s.profiles(), CUT)
    inp.participantBodies = [b for b in c.bRepBodies]
    inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(cm(p['INSERT_DEPTH']))),
                         adsk.fusion.ExtentDirections.NegativeExtentDirection)
    ex.add(inp).name = 'inserto_presilha_cabo'

    # ---------- carcaca: flange + tubo + 3 orelhas
    o, c = new_comp(root, 'carcaca')
    occs['carcaca'] = o
    circ_xy(c, [(0, 0)], p['case_D'], 0, W, NEW, 'carcaca')
    rect_xy(c, bx0, bx1, -by, by, 0, W, JOIN)
    rect_xy(c, tab_x0, bx0 + 0.5, -6.0, 6.0, 0, W, JOIN)
    s = Sk(c, c.xYConstructionPlane)
    s.circle(0, 0, 0, p['case_D'])
    s.circle(0, 0, 0, p['case_D'] - 2 * W)
    extrude(c, ring_profile(s.sk), W, p['case_top'] - W, JOIN)
    ears = [uv(a, p['ear_R'], 0) for a in EAR_ANGLES]
    circ_xy(c, ears, p['ear_D'], 0, p['case_top'], JOIN)
    circ_xy(c, [(0, 0)], p['flange_hole_D'], -1, W + 2, CUT)
    circ_xy(c, FL_SCREWS, p['SCREW_M3'], -1, W + 2, CUT)
    circ_xy(c, ears, p['INSERT_M3'], p['case_top'] - p['INSERT_DEPTH'], p['INSERT_DEPTH'] + 1, CUT)

    # ---------- disco espiral
    o, c = new_comp(root, 'disco_espiral')
    occs['disco'] = o
    z_disc = p['HORN_T']
    circ_xy(c, [(0, 0)], p['disc_D'], z_disc, p['disc_T'], NEW, 'disco_espiral')
    sk = c.sketches.add(c.xYConstructionPlane)
    hw = (p['pin_D'] + 2 * p['slot_clear']) / 2
    th = math.radians(p['spiral_deg'])
    rmin, rmax = p['r_pin_min'], p['r_pin_max']
    for a in JAW_ANGLES:
        ar = math.radians(a)

        def ctr(t):
            r = rmin + (rmax - rmin) * t
            f = ar + th * (1 - t)
            return r * math.cos(f), r * math.sin(f)

        n = 30
        outer, inner = adsk.core.ObjectCollection.create(), adsk.core.ObjectCollection.create()
        tang = []
        for i in range(n + 1):
            t = i / n
            x, y = ctr(t)
            xa, ya = ctr(min(t + 1e-4, 1.0))
            xb, yb = ctr(max(t - 1e-4, 0.0))
            tx, ty = xa - xb, ya - yb
            m = math.hypot(tx, ty)
            tx, ty = tx / m, ty / m
            tang.append((tx, ty))
            outer.add(P3(x - ty * hw, y + tx * hw))
            inner.add(P3(x + ty * hw, y - tx * hw))
        S = sk.sketchCurves.sketchFittedSplines
        so = S.add(outer)
        si = S.add(inner)
        x, y = ctr(0.0)
        tx, ty = tang[0]
        sk.sketchCurves.sketchArcs.addByThreePoints(so.startSketchPoint, P3(x - tx * hw, y - ty * hw), si.startSketchPoint)
        x, y = ctr(1.0)
        tx, ty = tang[-1]
        sk.sketchCurves.sketchArcs.addByThreePoints(so.endSketchPoint, P3(x + tx * hw, y + ty * hw), si.endSketchPoint)
    C = sk.sketchCurves.sketchCircles
    C.addByCenterRadius(P3(0, 0), cm(p['disc_center_hole'] / 2))
    for k in range(4):
        aa = math.radians(p['horn_phase_deg'] + 90 * k)
        C.addByCenterRadius(P3(p['HORN_PCD'] / 2 * math.cos(aa), p['HORN_PCD'] / 2 * math.sin(aa)), cm(p['SCREW_M3'] / 2))
    col = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count):
        col.add(sk.profiles.item(i))
    extrude(c, col, z_disc, p['disc_T'], CUT)

    # ---------- placa-guia com 3 rasgos radiais e 3 orelhas
    o, c = new_comp(root, 'placa_guia')
    occs['placa'] = o
    zp = p['case_top']
    circ_xy(c, [(0, 0)], p['case_D'], zp, p['plate_T'], NEW, 'placa_guia')
    circ_xy(c, ears, p['ear_D'], zp, p['plate_T'], JOIN)
    s = Sk(c, c.xYConstructionPlane)
    sw = p['jaw_W'] / 2 + T
    u0 = rmin - p['jaw_half_L'] - T
    u1 = rmax + p['jaw_half_L'] + T
    for a in JAW_ANGLES:
        s.poly([uv(a, u0, -sw) + (0,), uv(a, u1, -sw) + (0,), uv(a, u1, sw) + (0,), uv(a, u0, sw) + (0,)])
    extrude(c, s.profiles(), zp, p['plate_T'], CUT)
    circ_xy(c, ears, p['SCREW_M3'], zp - 1, p['plate_T'] + 2, CUT)

    # ---------- mordentes (posicao aberta)
    zf = zp + p['plate_T']
    zbl = zf + p['jaw_flange_T']
    for i, a in enumerate(JAW_ANGLES):
        o, c = new_comp(root, 'mordente_%d' % (i + 1))
        occs['mordente_%d' % (i + 1)] = o
        rp = rmax
        hl = p['jaw_half_L']
        jw = p['jaw_W'] / 2
        bl_in = rp - hl - p['blade_offset']
        fw = p['jaw_flange_W'] / 2
        bw = p['blade_w'] / 2

        def box(u0_, u1_, v0_, v1_, z0_, h_, op, name=None):
            s = Sk(c, c.xYConstructionPlane)
            s.poly([uv(a, u0_, v0_) + (0,), uv(a, u1_, v0_) + (0,), uv(a, u1_, v1_) + (0,), uv(a, u0_, v1_) + (0,)])
            return extrude(c, s.sk.profiles.item(0), z0_, h_, op, name)

        box(rp - hl, rp + hl, -jw, jw, zp, p['plate_T'], NEW, 'mordente_%d' % (i + 1))
        box(bl_in, rp + hl, -fw, fw, zf, p['jaw_flange_T'], JOIN)
        cxp, cyp = uv(a, rp, 0)
        circ_xy(c, [(cxp, cyp)], p['pin_D'], z_disc + 0.5, zp - z_disc - 0.5, JOIN)
        box(bl_in, bl_in + p['blade_t'], -bw, bw, zbl, p['blade_L'], JOIN)
        box(bl_in - p['pad_t'], bl_in, -bw, bw, zbl + p['blade_L'] - p['pad_L'], p['pad_L'], NEW, 'ponta_TPU_%d' % (i + 1))
    return d, occs


def run(_context: str):
    import os
    d, occs = build()
    out = r'C:\Users\jpinh\MK1\01_imprimir\03_garra'
    os.makedirs(out, exist_ok=True)
    em = d.exportManager
    for b in occs['garra_base'].component.bRepBodies:
        print(b.name, round(b.volume*1000))
    o = em.createSTLExportOptions(occs['garra_base'], os.path.join(out, 'garra_base.stl'))
    o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    em.execute(o)
    print('ok', [o.component.name for o in occs.values()])
