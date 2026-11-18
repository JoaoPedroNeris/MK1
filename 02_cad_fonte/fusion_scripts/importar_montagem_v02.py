"""Abre a montagem completa do MK I v0.2 (malhas) num documento novo do Fusion."""
import adsk.core, adsk.fusion, os, json
app = adsk.core.Application.get()
DIR = os.path.join(os.path.expanduser('~'), 'MK1', '05_visualizacao_fusion', 'montagem_b')
GROUPS = {'base': '1_base_e_eletronica', 'turret': '2_torre', 'upper': '3_braco', 'fore': '4_antebraco', 'garra': '5_garra'}

def run(_context):
    man = json.load(open(os.path.join(DIR, 'manifest.json')))
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.name = 'MK1_montagem_v02b'
    d = adsk.fusion.Design.cast(app.activeProduct)
    d.designType = adsk.fusion.DesignTypes.DirectDesignType
    d.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    root = d.rootComponent
    lib = None
    for i in range(app.materialLibraries.count):
        L = app.materialLibraries.item(i)
        if L.appearances.count > 50: lib = L; break
    base_ap = lib.appearances.itemByName('ABS (Branco)') if lib else None
    cache = {}
    def appear(c):
        key = tuple(round(v, 3) for v in c)
        if key in cache: return cache[key]
        if base_ap is None: return None
        a = d.appearances.addByCopy(base_ap, 'mk1_%d_%d_%d' % tuple(int(v * 255) for v in key))
        for j in range(a.appearanceProperties.count):
            p = a.appearanceProperties.item(j)
            if isinstance(p, adsk.core.ColorProperty):
                p.value = adsk.core.Color.create(*[int(v * 255) for v in key], 255); break
        cache[key] = a; return a
    occs = {}
    for g, nm in GROUPS.items():
        o = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); o.component.name = nm; occs[g] = o
    n = 0
    for it in man:
        o = occs.get(it['group'], occs['base'])
        sub = o.component.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        sub.component.name = it['name'] + ('' if it['printed'] else ' (ref)')
        mb = sub.component.meshBodies.add(os.path.join(DIR, it['file']), adsk.fusion.MeshUnits.MillimeterMeshUnit)
        a = appear(it['color'])
        if a:
            for k in range(mb.count): mb.item(k).appearance = a
        n += 1
    vp = app.activeViewport
    vp.camera = vp.camera
    cam = vp.camera
    cam.viewOrientation = adsk.core.ViewOrientations.IsoTopRightViewOrientation
    cam.isFitView = True
    vp.camera = cam
    print('importados', n)
