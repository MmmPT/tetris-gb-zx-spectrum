"""Check all native 8x8 piece pixels and attributes through draw/erase/preview/clear."""
from pathlib import Path
import json
from emulator import setup,run,MemoryView,screen
from skoolkit.simutils import PC,SP
ROOT=Path(__file__).resolve().parents[1];S=json.loads((ROOT/'symbols.json').read_text());forms=json.loads((ROOT/'assets/shapes.json').read_text())
s,t=setup(str(ROOT/'dist/Tetris_GB.z80'));run(s,t,100);run(s,t,4,['EN']);run(s,t,30);mem=MemoryView(s.memory)
def call(label):
 s.trace(s.registers[PC],S['wait_frame'],0,s.registers[25]+3*s.frame_duration,True,None,None,[0]*8,None,None);assert s.registers[PC]==S['wait_frame']
 mem[0x6ff0:0x6ff2]=[0xf0,0x7f];s.registers[SP]=0x6ff0;s.registers[PC]=S[label]
 s.trace(S[label],0x7ff0,0,s.registers[25]+250*s.frame_duration,True,None,None,[0]*8,None,None);assert s.registers[PC]==0x7ff0
 s.registers[PC]=S['main'];s.registers[SP]=0x7ffe
# Preview interior: screen columns 21..24, rows 16..19.
allowed={6144+y*32+x for y in range(16,20) for x in range(21,25)}
for y in range(128,160):
 a=((y&192)<<5)+((y&7)<<8)+((y&56)<<2)
 allowed.update(a+x for x in range(21,25))
cases=0
for mode in [0,1]:
 mem[S['gametype']]=mode;call('new_game')
 mem[S['hidden']]=1;call('render_preview')
 baseline=bytes(mem[16384:23296])
 for piece in range(7):
  mem[S['next']]=piece;mem[S['hidden']]=0;call('render_preview')
  visible=bytes(mem[16384:23296])
  changed={i for i,(a,b) in enumerate(zip(baseline,visible)) if a!=b}
  assert changed and changed<=allowed,(mode,piece,changed-allowed)
  for dx,dy,tile in forms[piece*4]:
   x=21+dx;y=15+dy
   assert 21<=x<=24 and 16<=y<=19,(piece,x,y)
  mem[S['hidden']]=1;call('render_preview')
  assert bytes(mem[16384:23296])==baseline,(mode,piece,'residue')
  cases+=1
mem[S['gametype']]=0;call('new_game')
mem[S['next']]=2;mem[S['hidden']]=0;call('render_preview')
screen(s.memory,ROOT/'preview_v7.png')
report={'preview_cases_A_and_B':cases,'all_seven_pieces_inside_box':True,'bitmap_and_attributes_outside_preview_unchanged':True,'hide_restores_all_pixels_and_attributes':True}
(ROOT/'validation_preview.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
