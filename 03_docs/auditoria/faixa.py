"""Faixa livre de ombro, cotovelo e punho (garra_base STL) - roda dentro da pasta do cad."""
import sys, os, numpy as np, trimesh
sys.path.insert(0, os.getcwd())
import assembly as A, parts as P
from params import *
from csg import sample_inside
def coll(moving_pts, fixed, off, angs, thr=0.3, mn=20):
    res={}
    for sgn in (1,-1):
        last=0
        for th in angs:
            t=np.radians(sgn*th); c,s=np.cos(t),np.sin(t); p=moving_pts
            q=np.c_[p[:,0]*c-p[:,2]*s+off[0], p[:,1]+off[1], p[:,0]*s+p[:,2]*c+off[2]]
            hit=sum(int((f.sdf(q)<-thr).sum()) for f in fixed)
            if hit>mn: break
            last=sgn*th
        res['+' if sgn>0 else '-']=last
    return res
angs=np.arange(0,181,2.5)
up=np.vstack([sample_inside(A.part(n),60000) for n in ("upper_arm","upper_cover")])
fo=np.vstack([sample_inside(A.part(n),60000) for n in ("forearm","fore_cover")])
cap=A.part("servo_cap")
out={}
out['ombro']=coll(up,[A.part("turret"),cap.move(SHOULDER_X,SH_OFF,SHOULDER_Z),cap.move(SHOULDER_X,-SH_OFF,SHOULDER_Z)],(SHOULDER_X,0,SHOULDER_Z),angs)
out['cotovelo']=coll(fo,[A.part("upper_arm"),A.part("upper_cover"),cap.move(L1,0,0)],(L1,0,0),angs)
gm=trimesh.load(sys.argv[1]); gp=trimesh.sample.sample_surface(gm,60000)[0]
# garra -> punho: X=z+71.5, Y=x, Z=y
gp=np.c_[gp[:,2]+71.5,gp[:,0],gp[:,1]]
out['punho']=coll(gp,[A.part("forearm"),A.part("fore_cover"),cap.move(L2,0,0)],(L2,0,0),angs)
print(out)
