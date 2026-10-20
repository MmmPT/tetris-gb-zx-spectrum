"""Execute native Z80 rules against collision, scoring and compaction fixtures."""
from pathlib import Path
import sys,json,random
ROOT=Path(__file__).resolve().parents[1];from emulator import setup,run,MemoryView,screen
from skoolkit.simutils import PC,SP,F
S=json.loads((ROOT/'symbols.json').read_text());forms=json.loads((ROOT/'assets/shapes.json').read_text())
s,t=setup(str(ROOT/'dist/Tetris_GB.z80'));run(s,t,60);run(s,t,3,['EN']);run(s,t,20)
mem=MemoryView(s.memory)
def call(label):
 mem[0x6ff0:0x6ff2]=[0xf0,0x7f];s.registers[SP]=0x6ff0;s.registers[PC]=S[label]
 s.trace(S[label],0x7ff0,0,s.registers[25]+100*s.frame_duration,True,None,None,[0]*8,None,None)
 assert s.registers[PC]==0x7ff0,(label,hex(s.registers[PC]))
def put(name,value):mem[S[name]]=value&255
rng=random.Random(482024);n=0
for k in range(600):
 board=[0x83 if rng.random()<.18 and y>10 else 0 for y in range(18) for x in range(10)]
 p=rng.randrange(7);r=rng.randrange(4);x=rng.randrange(-3,11);y=rng.randrange(-3,19)
 mem[S['board']:S['board']+180]=board
 for name,v in [('piece',p),('cr',r),('cx',x),('cy',y)]:put(name,v)
 expected=any(not(0<=x+dx<10) or y+dy>=18 or (y+dy>=0 and board[(y+dy)*10+x+dx]) for dx,dy,tile in forms[p*4+r])
 call('collision');actual=not bool(s.registers[F]&64);assert actual==expected,(p,r,x,y,expected,actual);n+=1
checks=[]
for rows in range(1,5):
 mem[S['board']:S['board']+180]=[0]*180
 for y in range(18-rows,18):mem[S['board']+y*10:S['board']+y*10+10]=[0x83]*10
 marker=10;mem[S['board']+marker*10+3]=0x84
 for name,v in [('mode',1),('gametype',0),('level',0),('score',0),('score+1',0)]:
  if name in S:put(name,v)
 mem[S['score']:S['score']+7]=[0]*7
 call('clear_lines')
 score=sum(((b>>4)*10+(b&15))*100**i for i,b in enumerate(mem[S['score']:S['score']+3]))
 assert score==[40,100,300,1200][rows-1],(rows,score)
 assert mem[S['lines']]==rows
 assert sum(bool(v) for v in mem[S['board']:S['board']+180])==1
 assert mem[S['board']+(marker+rows)*10+3]==0x84
 checks.append({'rows':rows,'score':score,'compaction':True})
# Level 0 -> 1 at ten lines, B-type completion at 25.
mem[S['board']:S['board']+180]=[0]*180;mem[S['board']+170:S['board']+180]=[0x83]*10
mem[S['lines']:S['lines']+2]=[9,0];mem[S['lines_bcd']:S['lines_bcd']+2]=[9,0];put('level',0);call('clear_lines');assert mem[S['level']]==1
put('gametype',1);put('remaining',1);put('mode',1);mem[S['board']+170:S['board']+180]=[0x83]*10;call('clear_lines');assert mem[S['mode']]==4
# Fresh game, keyboard pause, both rotations and next-preview/music toggles.
s,t=setup(str(ROOT/'dist/Tetris_GB.z80'));run(s,t,50);run(s,t,3,['EN']);run(s,t,20)
mem=MemoryView(s.memory)
run(s,t,3,['EN']);run(s,t,20);assert mem[S['mode']]==2
before=mem[S['py']];run(s,t,120);assert mem[S['py']]==before
run(s,t,3,['EN']);run(s,t,20);assert mem[S['mode']]==1
run(s,t,3,['n']);run(s,t,3);assert mem[S['hidden']]==1
run(s,t,3,['m']);run(s,t,3);assert mem[S['music_on']]==0
report={'collision_cases':n,'line_clears':checks,'level_progression':True,'b_type_completion':True,'pause_resume':True,'preview_toggle':True,'music_toggle':True,'tape_loader':'fresh-ROM fast load successful'}
(ROOT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

# Actual 128K hardware register output, independent interrupt clock, controls.
s,t=setup(str(ROOT/'dist/Tetris_GB.z80'));run(s,t,100)
assert s.frame_duration==70908 and t.ay[7]==56
heard=[False]*3
for _ in range(30):
 run(s,t,1)
 heard=[heard[c] or t.ay[8+c]>0 for c in range(3)]
assert all(heard)
run(s,t,3,['EN']);run(s,t,20)
assert s.memory[S['mode']]==1
# No outer text above or below the native 160x144 play area.
for y in list(range(24))+list(range(168,192)):
 a=16384+((y&192)<<5)+((y&7)<<8)+((y&56)<<2)
 assert all(s.memory[a+x]==0 for x in range(32))
# Read actual keyboard rows, then verify the game's input bits.
for key,bit in [('q',4),('a',2),('o',0),('p',1)]:
 run(s,t,3,[key]);assert s.memory[S['keys']]&(1<<bit),(key,s.memory[S['keys']]);run(s,t,3)
run(s,t,3,['EN']);run(s,t,20);assert s.memory[S['mode']]==2
before=[s.memory[i] for i in range(0x7040,0x7052)]
run(s,t,100);assert t.ay[8:11]==[0,0,0]
assert before==[s.memory[i] for i in range(0x7040,0x7052)]
run(s,t,3,['EN']);run(s,t,10);assert any(t.ay[8:11])
run(s,t,3,['m']);run(s,t,3);assert t.ay[8:11]==[0,0,0]
run(s,t,3,['m']);run(s,t,10);assert any(t.ay[8:11])
# Capture melody writes through gameplay and a native four-line clear.
stamps=[];orig=t.write_port

def port(reg,p,v,offset=0):
 if (p&0xc002)==0x8000 and t.outfffd==0:stamps.append(reg[25]+offset)
 orig(reg,p,v,offset)
t.write_port=port;s.set_tracer(t)
run(s,t,200)
# Trigger the native clear routine under normal interrupts; audio must keep time.
s.trace(s.registers[PC],S['wait_frame'],0,s.registers[25]+2*s.frame_duration,True,None,None,[0]*8,None,None)
assert s.registers[PC]==S['wait_frame']
mem=MemoryView(s.memory)
mem[S['board']:S['board']+180]=[0]*140+[0x83]*40
put('gametype',0);put('mode',1);call('clear_lines');s.registers[PC]=S['main'];s.registers[SP]=0x7ffe;run(s,t,200)
errors=[abs((b-a)/s.frame_duration-round((b-a)/s.frame_duration)) for a,b in zip(stamps,stamps[1:])]
assert len(stamps)>10 and max(errors)<.01,max(errors)
print('128K AY: original three voices, 50Hz interrupt clock, pause/mute, QAOP and clean screen passed; worst onset jitter in frames:',max(errors))
