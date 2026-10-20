"""Drive the actual Z80 IN 1F path, independently of keyboard emulation."""
from pathlib import Path
import json
from emulator import setup,run,screen
ROOT=Path(__file__).resolve().parents[1];S=json.loads((ROOT/'symbols.json').read_text());results={}
s,t=setup(str(ROOT/'dist/Tetris_GB.z80'));joy=[0];original=t.read_port

def port(reg,p):return joy[0] if p&255==31 else original(reg,p)
t.read_port=port;s.set_tracer(t);run(s,t,100)
joy[0]=16;run(s,t,8);joy[0]=0;run(s,t,10);assert s.memory[S['mode']]==1
results['fire_starts_game']=True
for value,expected in [(0,0),(1,2),(2,1),(4,4),(8,0),(16,16),(17,18),(20,20),(255,0),(3,0),(12,0)]:
 joy[0]=value;run(s,t,3);assert s.memory[S['keys']]&31==expected,(value,s.memory[S['keys']]);joy[0]=0;run(s,t,3)
results['directions_fire_diagonals_and_invalid_port_values']=True
rot=s.memory[S['rot']];joy[0]=16;run(s,t,15);after=s.memory[S['rot']];assert after==(rot-1)%4
run(s,t,15);assert s.memory[S['rot']]==after
joy[0]=0;run(s,t,4);joy[0]=16;run(s,t,4);assert s.memory[S['rot']]==(after-1)%4
joy[0]=0;run(s,t,4);results['one_rotation_per_fire_press']=True
joy[0]=255;run(s,t,4,['o']);assert s.memory[S['keys']]&1;run(s,t,4)
results['qaop_works_without_kempston']=True
run(s,t,6,['1']);run(s,t,6);assert s.memory[S['mode']]==0
run(s,t,4,['k']);run(s,t,4);assert s.memory[0x703d]==0
joy[0]=16;run(s,t,12);assert s.memory[S['mode']]==0
joy[0]=0;run(s,t,4,['k']);run(s,t,4);assert s.memory[0x703d]==1
joy[0]=16;run(s,t,8);joy[0]=0;run(s,t,8);assert s.memory[S['mode']]==1
results['menu_k_toggle']=True
screen(s.memory,ROOT/'v4_clean_hud.png')
(ROOT/'validation_kempston.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
