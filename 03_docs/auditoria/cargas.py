import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "02_cad_fonte", "cad"))
import numpy as np, json
from auditoria import props, torques, TIP, G, KGCM
from params import *
pr,_=props()
mu,xu=pr["upper"]; mf,xf=pr["fore"]; mh,xh=pr["hand"]
H=2*ACRYLIC+SHELL_Z+LS_T+SHOULDER_Z
print("altura do eixo do ombro acima da mesa",H)
out={}
# poses de pegar na mesa com a garra apontando para baixo; ponta a 15 mm da mesa
zw=-H+15+TIP+8   # punho acima do ponto de pega
print("z punho rel ombro",zw)
rows=[]
for r in (120,160,200,240,280):
    d=np.hypot(r,zw); c2=(d*d-L1*L1-L2*L2)/(2*L1*L2)
    if abs(c2)>1: rows.append((r,None)); continue
    t2=-np.arccos(c2)   # cotovelo para cima
    t1=np.arctan2(zw,r)-np.arctan2(L2*np.sin(t2),L1+L2*np.cos(t2))
    th1,th2=np.degrees(t1),np.degrees(t2); th3=-90-th1-th2
    t0=torques(pr,0,th1,th2,th3); t1k=torques(pr,1000,th1,th2,th3)-t0
    lim=lambda L,i:(L-abs(t0[i]))/abs(t1k[i])*1000 if abs(t1k[i])>1e-6 else 9999
    rows.append(dict(r=r,ombro=round(th1),cotovelo=round(th2),punho=round(th3),t0=[round(abs(v),1) for v in t0],
        max50=round(min(lim(20,0),lim(10,1))),max70=round(min(lim(10/0.7,0),lim(10,1))),
        max_folga=round(min(lim(0.6*20,0),lim(6,1)))))
out["pega_na_mesa"]=rows
# viga em U (secao do braco), sem contar a tampa de baixo
W=BEAM_W; Hh=BEAM_H; t=WALL
rects=[(W,t,Hh/2-t/2),(t,Hh-t,(-t)/2),(t,Hh-t,(-t)/2)]  # topo + 2 lados
A=sum(b*h for b,h,_ in rects); zc=sum(b*h*z for b,h,z in rects)/A
I=sum(b*h**3/12+b*h*(z-zc)**2 for b,h,z in rects); c=max(Hh/2-zc,zc+Hh/2)
out["viga"]=dict(I_mm4=round(I),c_mm=round(c,1),W_mm3=round(I/c))
Wclv=2*(CLV_T*Hh**2/6)
E=2000.0
for p in (0,100,250,500):
    Ms=torques(pr,p)[0]*KGCM; Me=torques(pr,p)[1]*KGCM
    # deflexao: braco (160) engastado no ombro com carga na ponta F e momento Me; antebraco idem
    Fb=(mf+mh+p/1000)*G; Ff=(mh+p/1000)*G
    d_up=Fb*L1**3/(3*E*I)+Me*L1**2/(2*E*I)
    d_rot_up=(Fb*L1**2/(2*E*I)+Me*L1/(E*I))   # rad na ponta do braco
    Mw=torques(pr,p)[2]*KGCM
    d_fo=Ff*L2**3/(3*E*I)+Mw*L2**2/(2*E*I)
    reach=L2+TIP
    total=d_up+d_rot_up*reach+d_fo
    folga=np.radians(0.5)*(L1+L2+TIP)+np.radians(0.5)*(L2+TIP)+np.radians(0.5)*TIP
    out[f"p{p}"]=dict(M_ombro_Nmm=round(Ms),sigma_viga_MPa=round(Ms/(I/c),2),sigma_garfo_MPa=round(Ms/Wclv,2),
        parafuso_horn_N=round(Ms/2/(4*HORN_PCD/2)),deflexao_PETG_mm=round(total,2),folga_servos_mm=round(folga,1))
print(json.dumps(out,indent=1))
json.dump(out,open(os.path.join(os.path.dirname(__file__),'cargas.json'),'w'),indent=1)
