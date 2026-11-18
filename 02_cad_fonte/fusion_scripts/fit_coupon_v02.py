"""
MK I v0.2 - cupom de teste de encaixe, so M3. Sem paquimetro: conte os furos.
Placa (esquerda para a direita): 1-3 inserto M3 | 4-6 passante M3 | 7-9 piloto M3
v0.2b: sem mastro (webcam vai num movel), entao sem bloco alto nem furos 10-12.
Rode no Fusion. Cria um documento novo com user parameters.
"""
import adsk.core, adsk.fusion, os

app = adsk.core.Application.get()
ROWS = [('ins', (4.0, 4.2, 4.4)), ('pass', (3.2, 3.4, 3.6)), ('pil', (2.4, 2.6, 2.8))]


def build(export_dir=None):
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.name = 'MK1_fit_coupon_v02b'
    d = adsk.fusion.Design.cast(app.activeProduct)
    d.designType = adsk.fusion.DesignTypes.ParametricDesignType
    d.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    root = d.rootComponent
    mm = lambda v: v / 10.0
    P = d.userParameters

    def par(n, e, c=''):
        P.add(n, adsk.core.ValueInput.createByString(e), 'mm', c)

    par('TOL', '0.25 mm'); par('WALL', '3.2 mm')
    par('SV_L', '45.2 mm'); par('SV_W', '24.7 mm'); par('POLE_D', '19.05 mm')
    par('plate_L', '172 mm'); par('plate_W', '35 mm'); par('plate_T', '6 mm')
    par('block_L', '100 mm'); par('block_W', '32 mm'); par('block_T', '10 mm')
    par('ring_T', '10 mm'); par('cham', '1 mm')
    par('pocket_L', 'SV_L + 2 * TOL'); par('pocket_W', 'SV_W + 2 * TOL')
    par('ring_L', 'pocket_L + 2 * WALL'); par('ring_W', '32 mm')
    par('hole_top', 'ring_T', 'furos passantes em tudo (v0.1 deixava o mastro cego)')
    holes = []
    x = 8.0
    for tag, ds in ROWS:
        for i, dd in enumerate(ds):
            n = 'd_%s_%d' % (tag, i + 1)
            par(n, '%g mm' % dd)
            holes.append((n, x, 9.0))
            x += 8.0
        x += 6.0
    xy = root.xYConstructionPlane

    def rect(x0, x1, y0, y1, wexpr, hexpr):
        sk = root.sketches.add(xy)
        r = sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(mm(x0), mm(y0), 0), adsk.core.Point3D.create(mm(x1), mm(y1), 0))
        ls = [r.item(i) for i in range(4)]
        hor = [l for l in ls if abs(l.startSketchPoint.geometry.y - l.endSketchPoint.geometry.y) < 1e-9][0]
        ver = [l for l in ls if abs(l.startSketchPoint.geometry.x - l.endSketchPoint.geometry.x) < 1e-9][0]
        dm = sk.sketchDimensions
        a = dm.addDistanceDimension(hor.startSketchPoint, hor.endSketchPoint, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, adsk.core.Point3D.create(mm((x0 + x1) / 2), mm(y0 - 3), 0))
        a.parameter.expression = wexpr
        b = dm.addDistanceDimension(ver.startSketchPoint, ver.endSketchPoint, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, adsk.core.Point3D.create(mm(x0 - 3), mm((y0 + y1) / 2), 0))
        b.parameter.expression = hexpr
        return sk

    def extrude(sk, dist, op, name):
        e = root.features.extrudeFeatures
        inp = e.createInput(sk.profiles.item(0), op)
        inp.setDistanceExtent(False, adsk.core.ValueInput.createByString(dist))
        f = e.add(inp)
        f.name = name
        return f

    def chamfer_all(body):
        edges = adsk.core.ObjectCollection.create()
        for ed in body.edges:
            edges.add(ed)
        ci = root.features.chamferFeatures.createInput2()
        ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, adsk.core.ValueInput.createByString('cham'), True)
        root.features.chamferFeatures.add(ci)

    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    plate = extrude(rect(0, 172, 0, 35, 'plate_L', 'plate_W'), 'plate_T', NEW, 'placa').bodies.item(0)
    chamfer_all(plate)
    rx0, rl = 118.0, 45.7 + 6.4
    ring = extrude(rect(rx0, rx0 + rl, 34, 66, 'ring_L', 'ring_W'), 'ring_T', NEW, 'anel_servo').bodies.item(0)
    tools = adsk.core.ObjectCollection.create()
    tools.add(ring)
    cin = root.features.combineFeatures.createInput(plate, tools)
    cin.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    root.features.combineFeatures.add(cin)
    body = root.bRepBodies.item(0)
    body.name = 'fit_coupon'
    extrude(rect(rx0 + 3.2, rx0 + rl - 3.2, 50 - 12.6, 50 + 12.6, 'pocket_L', 'pocket_W'), 'ring_T', CUT, 'rasgo_servo')
    sk = root.sketches.add(xy)
    sk.name = 'furos'
    for n, cx, cy in holes:
        c = sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(mm(cx), mm(cy), 0), mm(1.0))
        dim = sk.sketchDimensions.addDiameterDimension(c, adsk.core.Point3D.create(mm(cx + 3), mm(cy + 3), 0))
        dim.parameter.expression = n
    e = root.features.extrudeFeatures
    col = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count):
        col.add(sk.profiles.item(i))
    inp = e.createInput(col, CUT)
    inp.setDistanceExtent(False, adsk.core.ValueInput.createByString('hole_top'))
    e.add(inp).name = 'furos_cupom'
    b0 = root.bRepBodies.item(0)
    bb = b0.boundingBox
    print('furos', sk.profiles.count, 'bbox', [round((bb.maxPoint.x - bb.minPoint.x) * 10, 2), round((bb.maxPoint.y - bb.minPoint.y) * 10, 2), round((bb.maxPoint.z - bb.minPoint.z) * 10, 2)])
    if export_dir:
        os.makedirs(export_dir, exist_ok=True)
        o = d.exportManager.createSTLExportOptions(b0, os.path.join(export_dir, 'fit_coupon_v02b.stl'))
        o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        d.exportManager.execute(o)
    return d


def run(_context: str):
    build(os.path.join(os.path.expanduser('~'), 'MK1', '01_imprimir', '00_teste_primeiro'))
