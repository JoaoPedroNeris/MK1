import sys, json, math, numpy as np, trimesh
from auditoria_furos import measure
G='/mnt/project-files/v0.2/stl/'
def ins_of(path):
    m=trimesh.load(G+path)
    return lambda p: m.contains(np.asarray(p,float).reshape(-1,3))
SV_L,SV_SHAFT_END,T,W=45.2,11.0,0.25,3.2
cx1=SV_L-SV_SHAFT_END+T; sx_r=cx1+10.6/2; bx1=cx1+10.6
FL=[(sx_r,9.0),(sx_r,-9.0),(-39.0,0.0)]
R4=2.1; R3=1.7
zj=-35.5-36
T={}
gb=[]
for i,(x,y) in enumerate(FL):
    gb.append(('flange %d (carcaça)'%(i+1),'inserto',(x,y,0),(0,0,-1),R4,6.5,False))
gb.append(('presilha do cabo (lateral)','inserto',(bx1,-3,-20),(-1,0,0),R4,6.5,False))
for s in (1,-1):
    for a in (45,135,225,315):
        gb.append(('horn garfo %s %d°'%('+X' if s>0 else '-X',a),'passante',(s*21,7*math.cos(math.radians(a)),zj+7*math.sin(math.radians(a))),(s,0,0),R3,5,True))
ca=[]
for a in (30,150,270):
    x,y=37.5*math.cos(math.radians(a)),37.5*math.sin(math.radians(a))
    ca.append(('orelha %d° (placa-guia)'%a,'inserto',(x,y,9),(0,0,-1),R4,6.5,False))
for i,(x,y) in enumerate(FL):
    ca.append(('furo flange %d'%(i+1),'passante',(x,y,3.2),(0,0,-1),R3,3.2,True))
pg=[]
for a in (30,150,270):
    x,y=37.5*math.cos(math.radians(a)),37.5*math.sin(math.radians(a))
    pg.append(('orelha %d°'%a,'passante',(x,y,15),(0,0,-1),R3,6,True))
di=[]
for k in range(4):
    aa=math.radians(35+90*k)
    di.append(('horn %d'%(k+1),'passante',(7*math.cos(aa),7*math.sin(aa),7.5),(0,0,-1),R3,4,True))
for nm,path,hs in [('garra_base',"cabos/garra_base.stl",gb),('carcaca','garra/carcaca.stl',ca),('placa_guia','garra/placa_guia.stl',pg),('disco_espiral','garra/disco_espiral.stl',di)]:
    f=ins_of(path); T[nm]=[]
    for (n,t,mo,ax,r,d,th) in hs:
        res=measure(f,mo,ax,r,d,th,n_ang=36)
        T[nm].append(dict(nome=n,tipo=t,**res))
        print(nm,'%-28s %-9s vazio=%s min=%.2f meio=%.2f fundo=%s dir=%s'%(n,t,res['furo_vazio'],res['parede_min'],res['parede_meio'],res.get('fundo','-'),res['direcao']),flush=True)
json.dump(T,open(sys.argv[1],'w'),indent=1,ensure_ascii=False)
