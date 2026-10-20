from skoolkit import CSimulator
from skoolkit.simutils import from_snapshot,get_state
from skoolkit.snapshot import Snapshot,write_snapshot
from skoolkit.trace import Tracer
from PIL import Image
import sys
keys=['CS z x c v','a s d f g','q w e r t','1 2 3 4 5','0 9 8 7 6','p o i u y','EN l k j h','SP SS m n b']
keys=[x.split() for x in keys]
def setup(path):
 s=Snapshot.get(path);sim=from_snapshot(CSimulator,s);tr=Tracer(sim,s.border,s.out7ffd,s.outfffd,list(s.ay),0,False);sim.set_tracer(tr);tr.keyboard=[0]*8;return sim,tr
def run(sim,tr,frames=50,pressed=[]):
 tr.keyboard=[sum(1<<j for j,k in enumerate(row) if k in pressed) for row in keys]
 sim.trace(sim.registers[24],None,0,sim.registers[25]+frames*sim.frame_duration,True,None,None,tr.keyboard,None,None)
def screen(mem,path):
 data=mem.banks[7][:6912] if hasattr(mem,'o7ffd') and mem.o7ffd&8 else [mem[i] for i in range(16384,23296)]
 im=Image.new('RGB',(256,192));p=im.load()
 for y in range(192):
  a=((y&192)<<5)+((y&7)<<8)+((y&56)<<2)
  for x in range(256):
   attr=data[6144+(y//8)*32+x//8];c=(attr&7) if data[a+x//8]&(128>>(x%8)) else ((attr>>3)&7);v=255 if attr&64 else 205
   p[x,y]=(v if c&2 else 0,v if c&4 else 0,v if c&1 else 0)
 im.resize((768,576),Image.Resampling.NEAREST).save(path)
def save(sim,path):write_snapshot(path,*get_state(sim))
if __name__=='__main__':
 sim,tr=setup(sys.argv[1]);run(sim,tr,int(sys.argv[3]) if len(sys.argv)>3 else 150);screen(sim.memory,sys.argv[2]+'.png');save(sim,sys.argv[2]+'.z80');open(sys.argv[2]+'.bin','wb').write(bytes(sim.memory))

class MemoryView:
 def __init__(self,m):self.m=m
 def __getitem__(self,k):
  if isinstance(k,slice):return [self.m[i] for i in range(*k.indices(65536))]
  return self.m[k]
 def __setitem__(self,k,v):
  if isinstance(k,slice):
   for i,a in zip(range(*k.indices(65536)),v):self.m[i]=a
  else:self.m[k]=v
