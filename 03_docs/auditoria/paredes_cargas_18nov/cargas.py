import json, numpy as np, trimesh, parts as P
from csg import mass_props
from params import *
G=9.81; RHO=1.27
def csg(node, fill):
    v,cg=mass_props(node,n=300_000); return v*RHO*fill, cg   # g, mm
def stl(path, fill, rho=RHO):
    m=trimesh.load('/mnt/project-files/v0.2/stl/'+path); return m.volume/1000*rho*fill, m.center_mass
res={}
for cen,(fill_link,fill_small) in {'otimista (25% preench.)':(0.55,0.8),'pessimista (40-60% preench.)':(0.75,0.95)}.items():
  out={}
  for nome,L,node in (('upper',L1,P.upper_arm()),('fore',L2,P.forearm())):
    items=[]
    m,cg=csg(node,fill_link); items.append(('elo',m,cg[0]))
    m,cg=csg(P.belly_cover(L),fill_small); items.append(('tampa baixo',m,cg[0]))
    m,cg=csg(P.armor(L),0.9); items.append(('2 placas laranja',2*m,cg[0]))
    m,cg=csg(P.servo_cap(),fill_small); items.append(('tampa servo',m,L+cg[0]))
    items.append(('servo distal',SV_MASS,L-(SV_L/2-SV_SHAFT_END)))
    m,cg=csg(P.presilha_cabo(),1.0); items.append(('2 presilhas',2*m,L/2))
    items.append(('parafusos+insertos (~12)',12*0.9,L/2))
    items.append(('cabo do barramento',10.0,L/2))
    out[nome]=items
  # garra (frame do punho: X = z_g + 71.5)
  g=[]
  for f,fl in [('cabos/garra_base.stl',fill_link),('garra/carcaca.stl',fill_small),('garra/disco_espiral.stl',fill_small),('garra/placa_guia.stl',fill_small)]:
    m,c=stl(f,fl); g.append((f.split('/')[-1][:-4],m,c[2]+71.5))
  mm=0;mx=0
  for i in (1,2,3):
    m,c=stl('garra/mordente_%d.stl'%i,0.95); mm+=m; mx+=m*(c[2]+71.5)
  g.append(('3 mordentes',mm,mx/mm))
  g.append(('servo da garra',SV_MASS,-17.5+71.5))
  g.append(('presilha+parafusos+TPU',2+9*0.9+3,40))
  out['garra']=g
  res[cen]=out
json.dump({k:{kk:[(a,round(b,1),round(c,1)) for a,b,c in vv] for kk,vv in v.items()} for k,v in res.items()},open('massas.json','w'),indent=1,ensure_ascii=False)
for k,v in res.items():
  print('==',k)
  for kk,vv in v.items():
    M=sum(b for a,b,c in vv); X=sum(b*c for a,b,c in vv)/M
    print('  %s massa %.0f g  CG %.1f mm'%(kk,M,X)); [print('     ',a,round(b,1),round(c,1)) for a,b,c in vv]
