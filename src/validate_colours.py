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
attrs={0x80:104,0x81:72,0x82:80,0x83:112,0x84:120,0x85:88,0x86:96,0x87:120,0x88:104,0x89:104,0x8a:104,0x8b:104,0x8f:104}
mem[S['board']:S['board']+180]=[0]*180;call('render_board')
for piece in range(7):
 for rot in range(4):
  for key,val in [('piece',piece),('rot',rot),('px',3),('py',4)]:mem[S[key]]=val
  call('draw_piece')
  for dx,dy,tile in forms[piece*4+rot]:
   x=11+dx;y=7+dy;assert mem[22528+y*32+x]==attrs[tile],(piece,rot,tile)
   a=16384+((y*8&192)<<5)+((y*8&56)<<2)+x
   assert bytes(mem[a+i*256] for i in range(8))==bytes([255,129,129,129,129,129,129,255])
  call('erase_piece')
  assert all(mem[22528+y*32+x]==56 for y in range(3,21) for x in range(8,18)),(piece,rot)
for piece in range(7):
 mem[S['next']]=piece;mem[S['hidden']]=0;call('render_preview')
 for dx,dy,tile in forms[piece*4]:assert mem[22528+(15+dy)*32+21+dx]==attrs[tile]
 mem[S['hidden']]=1;call('render_preview');assert all(mem[22528+y*32+x]==56 for y in range(16,20) for x in range(21,25))
mem[S['board']:S['board']+180]=[0]*140+[0x82]*40;mem[S['board']+103]=0x81;call('clear_lines');assert mem[22528+17*32+11]==72
assert mem[S['board']+143]==0x81
# Original side ornaments are dark, not invented checkerboard or empty white.
tiles=(ROOT/'assets/tiles.bin').read_bytes()
assert sum(v.bit_count() for v in tiles[0x2a*8:0x2b*8])>48
assert sum(v.bit_count() for v in tiles[0x2b*8:0x2c*8])>48
# Capture a real native scene with several differently coloured locked pieces.
mem[S['board']:S['board']+180]=[0]*180
placements=[(0,0,15),(1,5,15),(2,1,12),(3,6,12),(4,1,9),(5,5,9),(6,3,6)]
for p,x,y in placements:
 for dx,dy,tile in forms[p*4]:mem[S['board']+(y+dy)*10+x+dx]=tile
mem[S['mode']]=1;mem[S['gametype']]=0;mem[S['hidden']]=0;call('render_board');call('render_preview');call('hud')
screen(s.memory,ROOT/'v5_colour_scene.png')
report={'all_28_rotations_pixels_and_attributes':True,'erase_restores_empty_attributes':True,'all_seven_previews_and_hide':True,'line_clear_moves_colour_with_board':True,'original_dark_background_restored':True}
(ROOT/'validation_colours.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
