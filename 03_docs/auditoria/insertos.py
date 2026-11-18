import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "02_cad_fonte", "cad"))
import numpy as np, parts as P
from params import *
r=INSERT_M3/2
def wall(node,c,zmouth,zdir,depth=INSERT_L):
    zs=zmouth+zdir*np.linspace(1.2,depth-0.3,6); best=(99,None)
    for z in zs:
        for a in np.radians(np.arange(0,360,5)):
            d=np.array([np.cos(a),np.sin(a)])
            t=np.arange(r+0.05,15,0.05)
            pts=np.c_[c[0]+d[0]*t,c[1]+d[1]*t,np.full_like(t,z)]
            s=node.sdf(pts); out=np.where(s>0)[0]
            th=t[out[0]]-r if len(out) else 15
            if th<best[0]: best=(round(th,2),(round(np.degrees(a)),round(z,1)))
    return best
xf,xb=POCKET_X1+END_WALL/2,POCKET_X0-END_WALL/2
res={}
up=P.upper_arm(); fo=P.forearm(); tu=P.turret(); sh=P.base_shell()
for nm,node,L in (("braco",up,L1),("antebraco",fo,L2)):
    for (x,y) in [(xf,0),(xb,12),(xb,-12)]:
        res[f"{nm}: bolso do servo ({x:.1f},{y})"]=wall(node,(L+x,y),POCKET_Z,-1)
    for x in (BRIDGE_X1+3,L+P.PX0+3):
        res[f"{nm}: tampa de baixo x={x:.1f}"]=wall(node,(x,0),-BEAM_H/2,1)
for s in (1,-1):
    for (x,y) in [(xf,0),(xb,12),(xb,-12)]:
        res[f"torre: bolso ombro {s:+d} ({x:.1f},{y})"]=wall(tu,(SHOULDER_X+x,s*SH_OFF+y),SHOULDER_Z+POCKET_Z,-1)
xr=SHOULDER_X+P.PX0
res["torre: presilha"]=wall(tu,(xr+(TCLIP_X[0]+TCLIP_X[1])/2,TCLIP_Y[0]+CLIP_ABA/2+1),TCLIP_Z0+TCLIP_H,-1)
px,py=P.lid_corners()[0]
res["base: canto (cima)"]=wall(sh,(px,py),SHELL_Z,-1)
res["base: canto (baixo)"]=wall(sh,(px,py),0,1)
for k,v in res.items(): print(f"{k:45s} {v}")
