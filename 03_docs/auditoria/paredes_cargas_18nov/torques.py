import json, numpy as np
from params import *
M=json.load(open('massas.json'))
G=9.81; KG=G*10/1000  # N.mm -> kg.cm : divide by 98.1
XP=71.5+50.7   # centro do objeto entre as pontas, a partir do eixo do punho
def grp(c,k,smass=SV_MASS):
    it=M[c][k]; m=0;mx=0
    for a,b,x in it:
        if a.startswith('servo'): b=smass
        m+=b; mx+=b*x
    return m/1000, mx/m
def torques(c,th1,th2,th3,pay,smass=SV_MASS):
    mu,xu=grp(c,'upper',smass); mf,xf=grp(c,'fore',smass); mg,xg=grp(c,'garra',smass)
    a1=np.radians(th1);a2=a1+np.radians(th2);a3=a2+np.radians(th3)
    el=L1*np.cos(a1); wr=el+L2*np.cos(a2)
    pts=[(mu,xu*np.cos(a1),'u'),(mf,el+xf*np.cos(a2),'f'),(mg,wr+xg*np.cos(a3),'g'),(pay,wr+XP*np.cos(a3),'p')]
    ts=sum(m*G*x for m,x,_ in pts)/98.1
    te=sum(m*G*(x-el) for m,x,n in pts if n!='u')/98.1
    tw=sum(m*G*(x-wr) for m,x,n in pts if n in 'gp')/98.1
    return ts,te,tw
out={}
for c in M:
  for sm in (55.0,69.0):
    key='%s, servo %d g'%(c,sm)
    t0=torques(c,0,0,0,0,sm); t1=torques(c,0,0,0,0.1,sm); tpay=torques(c,0,0,0,1.0,sm)
    dp=[tpay[i]-t0[i] for i in range(3)]  # kg.cm por kg de carga
    caps={}
    for nome,lim in {'nominal 10 kg.cm (contínuo)':(10*2*0.8,10,10),'1/2 do travamento c/ fator dinâmico 1,3':(15*2*0.8/1.3,15/1.3,15/1.3)}.items():
        caps[nome]=[round(1000*(lim[i]-t0[i])/dp[i]) for i in range(3)]
    out[key]=dict(esticado_sem_carga=[round(x,2) for x in t0],esticado_100g=[round(x,2) for x in t1],carga_max_g_esticado=caps)
    print(key, out[key])
# poses reais: pegar da mesa, garra apontando para baixo
H=6.35+SHELL_Z+ACRYLIC+LS_T+TURRET_T+SHOULDER_Z-TURRET_T  # altura do eixo do ombro sobre a mesa (aprox)
print('altura ombro ~',H)
def ik(R,zt):
    # punho acima do ponto de pega: garra vertical para baixo; ponto de pega a XP do punho
    wx,wz=R-SHOULDER_X, zt+XP-H
    d=np.hypot(wx,wz)
    if d>L1+L2-1: return None
    c2=(d*d-L1*L1-L2*L2)/(2*L1*L2); t2=-np.arccos(c2)  # cotovelo para cima
    t1=np.arctan2(wz,wx)-np.arctan2(L2*np.sin(t2),L1+L2*np.cos(t2))
    t3=-90-np.degrees(t1+t2)
    return np.degrees(t1),np.degrees(t2),t3
tab=[]
c=list(M)[1]
for R in range(120,381,20):
    s=ik(R,25)
    if s is None: tab.append((R,None)); continue
    t0=torques(c,*s,0); t2=torques(c,*s,0.2)
    dp=[(torques(c,*s,1)[i]-t0[i]) for i in range(3)]
    cap=[ (1000*(lim-abs(t0[i]))/abs(dp[i]) if abs(dp[i])>1e-6 else 9999) for i,lim in enumerate((16,10,10))]
    tab.append((R,[round(x) for x in s],[round(abs(x),1) for x in t0],[round(abs(x),1) for x in t2],round(min(cap))))
    print(R,tab[-1][1:])
out['poses_mesa_pessimista']=tab
json.dump(out,open('torques.json','w'),indent=1,ensure_ascii=False)
