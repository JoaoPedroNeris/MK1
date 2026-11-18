import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "02_cad_fonte", "cad"))
import json, numpy as np, trimesh, glob, os
import assembly as A, parts as P
from csg import mass_props
from params import *
G=9.81; KGCM=G*10  # N.mm por kg.cm
RATED=10.0; STALL=30.0
ZERO=dict(yaw=0,shoulder=0,elbow=0,wrist=0)
# extras nao modelados (HIPOTESES): parafusos/insertos/cabo por grupo, g, e posicao x no elo
# upper: 3 insertos+3 M3x10 tampa cotovelo, 8 M3 horns ombro, 2 M3x14 tampa, cabo ~200 mm (~6 g)
EXTRA={"upper":[("fixadores",10.0,None),("cabo",6.0,80.0)],
       "fore":[("fixadores",8.0,None),("cabo",6.0,75.0)],
       "hand":[("fixadores",8.0,40.0),("cabo",3.0,20.0)]}
def props(fill_scale=1.0):
    items=A.build(ZERO); f=A.frames(dict(A.DEFAULT_POSE,**ZERO))
    out={}; detail={}
    for g in ("upper","fore"):
        inv=np.linalg.inv(f[g]); mt=0; mom=np.zeros(3); det=[]
        for name,node,color,printed,grp,m in items:
            if grp!=g: continue
            if printed:
                _,q,proc,mat,rho,fill,_=A.PARTS[name]
                vol,cl=mass_props(A.part(name),n=200_000)
                mass=vol*rho*min(1,fill*fill_scale)/1000; cw=m@np.r_[cl,1]
            elif name=="sts3215":
                mass=SV_MASS/1000; lo,hi=node.aabb(); cw=np.r_[(lo+hi)/2,1]
            else: continue
            p=(inv@cw)[:3]; mt+=mass; mom+=mass*p; det.append((name,round(mass*1000,1),round(p[0],1)))
        cg=mom/mt
        for n,gm,x in EXTRA[g]:
            x=cg[0] if x is None else x; mom[0]+=gm/1000*x; mt+=gm/1000; det.append((n,gm,x))
        out[g]=(mt,mom[0]/mt); detail[g]=det
    # garra: STLs (referencial garra, X_punho = z+71.5)
    dens={"garra_base":(1.27,0.75),"carcaca":(1.27,0.75),"disco_espiral":(1.27,0.85),"placa_guia":(1.27,0.75),"mordente":(1.27,1.0),"ponta":(1.21,1.0)}
    mt=0;mx=0;det=[]
    for fn in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','01_imprimir','03_garra','*.stl'))):
        nm=os.path.basename(fn)[:-4]; tm=trimesh.load(fn)
        key=[k for k in dens if nm.startswith(k)][0]; rho,fill=dens[key]
        mass=tm.volume/1000*rho*min(1,fill*fill_scale)/1000; x=tm.center_mass[2]+71.5
        mt+=mass; mx+=mass*x; det.append((nm,round(mass*1000,1),round(x,1)))
    # servo da garra: eixo na origem, corpo de z=-35 a 0
    for n,gm,x in [("sts3215_garra",SV_MASS,-17.5+71.5),("pinos/parafusos",8.0,40.0),("cabo",3.0,20.0),("presilha",1.0,50.0)]:
        mt+=gm/1000; mx+=gm/1000*x; det.append((n,gm,x))
    out["hand"]=(mt,mx/mt); detail["hand"]=det
    return out,detail
TIP=122.0  # centro das pontas TPU (X a partir do eixo do punho)
def torques(pr,payload_g,th1=0,th2=0,th3=0):
    a1=np.radians(th1);a2=a1+np.radians(th2);a3=a2+np.radians(th3)
    el=L1*np.cos(a1); wr=el+L2*np.cos(a2)
    pts=[(pr["upper"][0],pr["upper"][1]*np.cos(a1)),(pr["fore"][0],el+pr["fore"][1]*np.cos(a2)),
         (pr["hand"][0],wr+pr["hand"][1]*np.cos(a3)),(payload_g/1000,wr+TIP*np.cos(a3))]
    ts=sum(m*G*x for m,x in pts); te=sum(m*G*(x-el) for m,x in pts[1:]); tw=sum(m*G*(x-wr) for m,x in pts[2:])
    return np.array([ts,te,tw])/KGCM
if __name__=="__main__":
    pr,det=props()
    res={"grupos":{g:{"massa_g":round(m*1000,1),"cg_x_mm":round(x,1)} for g,(m,x) in pr.items()},"detalhe":det}
    res["torque_esticado_kgcm"]={str(p):[round(v,2) for v in torques(pr,p)] for p in (0,100,250,500)}
    # carga maxima: ombro/2 servos, cotovelo, punho
    def maxload(limit_sh,limit_el,limit_wr):
        out=[]
        for lim,i in ((limit_sh,0),(limit_el,1),(limit_wr,2)):
            t0=torques(pr,0)[i]; dt=torques(pr,1000)[i]-t0
            out.append(round(max(0,(lim-t0)/dt*1000)))
        return out
    res["carga_max_g"]={}
    for nome,ush,frac in (("nominal 10, divisao 50/50",RATED,0.5),("nominal 10, divisao 70/30",RATED,0.7),("50% nominal (folga dinamica), 50/50",0.5*RATED,0.5),("50% nominal, 70/30",0.5*RATED,0.7)):
        k=RATED if ush==RATED else 0.5*RATED
        res["carga_max_g"][nome]=maxload(k/frac,k,k)
    # sensibilidade: preenchimento 100%
    pr2,_=props(1.6)
    res["sens_preench_alto"]={g:round(m*1000,1) for g,(m,x) in pr2.items()}
    res["torque_esticado_preench_alto"]={str(p):[round(v,2) for v in torques(pr2,p)] for p in (0,250)}
    json.dump(res,open(os.path.join(os.path.dirname(__file__),'auditoria.json'),'w'),indent=1,ensure_ascii=False)
    print(json.dumps(res,indent=1,ensure_ascii=False))
