"""Verify attribute-only flashing and real 128K shadow-screen presentation."""
from pathlib import Path
import json
from emulator import setup,run,MemoryView
from skoolkit.simutils import PC,SP
ROOT=Path(__file__).resolve().parents[1];S=json.loads((ROOT/'symbols.json').read_text())
s,t=setup(str(ROOT/'dist/Tetris_GB.z80'));run(s,t,100);run(s,t,4,['EN']);run(s,t,30);m=MemoryView(s.memory)
def call(label):
 s.trace(s.registers[PC],S['wait_frame'],0,s.registers[25]+3*s.frame_duration,True,None,None,[0]*8,None,None);assert s.registers[PC]==S['wait_frame']
 m[0x6ff0:0x6ff2]=[0xf0,0x7f];s.registers[SP]=0x6ff0;s.registers[PC]=S[label];start=s.registers[25]
 s.trace(S[label],0x7ff0,0,start+250*s.frame_duration,True,None,None,[0]*8,None,None);assert s.registers[PC]==0x7ff0
 s.registers[PC]=S['main'];s.registers[SP]=0x7ffe;return s.registers[25]-start
attributes={0x81:72,0x82:80,0x83:112,0x84:120,0x85:88,0x86:96}
rows=[17,16,14,12];board=[0]*180
for n,y in enumerate(rows):
 for x in range(10):board[y*10+x]=[0x81,0x82,0x83,0x84,0x85,0x86][(n+x)%6]
board[10*10+2]=0x81;m[S['board']:S['board']+180]=board;call('render_board')
base=bytes(s.memory.banks[5][:6912]);m[S['cleared']]=4
m[0x73c0:0x73c4]=rows
for i,y in enumerate(rows):m[0x7300+i*10:0x730a+i*10]=board[y*10:y*10+10]
cycles=[]
for phase in [1,0,1,0]:
 m[S['flash']]=phase;cycles.append(call('flash_completed_rows'));now=bytes(s.memory.banks[5][:6912]);assert now[:6144]==base[:6144]
 for y in range(24):
  for x in range(32):
   expected=base[6144+y*32+x]
   if y-3 in rows and 8<=x<18:expected=63 if phase else attributes[board[(y-3)*10+x-8]]
   assert now[6144+y*32+x]==expected,(phase,x,y)
assert max(cycles)<12000,cycles
# Run the entire native clear; watch the real 7FFD hardware port and both banks.
events=[];orig=t.write_port;stable=[None];shadow=[None];checks={'copy_stable':0,'shadow_stable':0,'atomic_flip':False}
def write(reg,p,v,offset=0):
 if (p&0x8002)==0:
  previous=s.memory.o7ffd
  if v==0x17:
   current=bytes(s.memory.banks[5][:6912])
   if stable[0] is None:stable[0]=current
   assert current==stable[0];checks['copy_stable']+=1
  if v==0x18:
   assert bytes(s.memory.banks[7][:6912])==bytes(s.memory.banks[5][:6912])
   shadow[0]=bytes(s.memory.banks[7][:6912])
  if v==0x10 and previous&8:
   assert bytes(s.memory.banks[7][:6912])==shadow[0]
   checks['atomic_flip']=True
  events.append((reg[25]+offset,v))
 elif s.memory.o7ffd&8 and shadow[0] is not None:
  assert bytes(s.memory.banks[7][:6912])==shadow[0];checks['shadow_stable']+=1
 orig(reg,p,v,offset)
t.write_port=write;s.set_tracer(t);m[S['mode']]=1;m[S['gametype']]=0;call('clear_lines')
assert checks['copy_stable']==216 and checks['shadow_stable']>0 and checks['atomic_flip'];assert s.memory.o7ffd==16
for y in range(24):
 for x in range(32):
  if not(3<=y<21 and 8<=x<18):assert s.memory.banks[5][6144+y*32+x]==base[6144+y*32+x]
report={'flash_changes_only_completed_row_attributes':True,'flash_bitmap_unchanged':True,'flash_cycles_max_four_rows':max(cycles),'screen_copy_chunks':checks['copy_stable'],'visible_shadow_stable_during_compaction':checks['shadow_stable'],'atomic_display_swap':checks['atomic_flip'],'paging_restored':True}
(ROOT/'validation_clear_animation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
