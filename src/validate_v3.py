"""Exercise native AY effects, menus, result tables, records, endings and attract mode."""
from pathlib import Path
import sys,json
from emulator import setup,run,MemoryView,screen
from skoolkit.simutils import PC,SP,A
ROOT=Path(__file__).resolve().parents[1];S=json.loads((ROOT/'symbols.json').read_text());results={}
def fresh():
 s,t=setup(str(ROOT/'dist/Tetris_GB.z80'));run(s,t,100);return s,t,MemoryView(s.memory)
def align():
 s.trace(s.registers[PC],S['wait_frame'],0,s.registers[25]+3*s.frame_duration,True,None,None,[0]*8,None,None)
 assert s.registers[PC]==S['wait_frame']
def call(label,a=None):
 align();mem[0x6ff0:0x6ff2]=[0xf0,0x7f];s.registers[SP]=0x6ff0;s.registers[PC]=S[label]
 if a is not None:s.registers[A]=a
 s.trace(S[label],0x7ff0,0,s.registers[25]+200*s.frame_duration,True,None,None,[0]*8,None,None)
 assert s.registers[PC]==0x7ff0,(label,hex(s.registers[PC]))
 s.registers[PC]=S['main'];s.registers[SP]=0x7ffe
def key(k):run(s,t,6,[k]);run(s,t,14)
s,t,mem=fresh();key('t');assert mem[S['music_choice']]==1;key('t');assert mem[S['music_choice']]==2;key('l');assert mem[S['heart']]==1;key('r');assert mem[S['mode']]==7;key('EN');assert mem[S['mode']]==0
screen(s.memory,ROOT/'v3_menu.png');results['menu_music_heart_records']=True
s,t,mem=fresh();key('EN');key('m');run(s,t,100);mem[S['mode']]=7
for ident in range(1,13):
 call('request_sfx',ident);heard=False
 for n in range(90):
  run(s,t,1)
  heard|=t.ay[9]>0
 assert heard,ident
 assert mem[S['sfx_active']]==0,(ident,mem[S['sfx_active']])
 assert t.ay[8:11]==[0,0,0],(ident,t.ay)
results['all_12_effects_with_music_off']=True
# Reject low-priority movement while playing Tetris; restore harmony afterwards.
key('m');call('request_sfx',7);run(s,t,2);call('request_sfx',4);run(s,t,2);assert mem[S['sfx_active']]==7;run(s,t,100);assert mem[S['sfx_active']]==0
results['effect_priority_and_release']=True
# B completion calls its real scoreboard via HUD.
mem[S['gametype']]=1;mem[S['remaining']]=1;mem[S['mode']]=1;mem[S['startlevel']]=3;mem[S['level']]=3
mem[S['board']:S['board']+180]=[0]*170+[0x83]*10
call('clear_lines');call('hud');assert mem[S['mode']]==5;assert mem[S['remaining']]==0;assert mem[S['stats']]>0
screen(s.memory,ROOT/'v3_b_results.png');key('EN');assert mem[S['mode']]==6
key('q');key('p');key('q');key('EN');assert mem[S['mode']]==7
ptr=mem[S['record_ptr']]+256*mem[S['record_ptr']+1];assert mem[ptr+3:ptr+5]==[11,11]
run(s,t,30);screen(s.memory,ROOT/'v3_records.png');results['b_scoreboard_and_named_records']=True
# All themes select valid streams and produce audio; oneshot themes stop.
s,t,mem=fresh();mem[S['mode']]=7
for song in range(14):
 call('select_song',song);vol=False
 for n in range(180):run(s,t,1);vol|=any(t.ay[8:11])
 assert vol,song
results['all_14_music_programs']=True
# Original endings render and exit; stamps must not overwrite attribute RAM.
for kind,score,height in [(0,0x10,0),(0,0x15,0),(0,0x20,0),(1,0,3),(1,0,5)]:
 s,t,mem=fresh();mem[S['gametype']]=kind;mem[S['score']+2]=score;mem[S['height']]=height
 call('show_ending');run(s,t,320);assert mem[S['mode']]==8
 assert all(v==56 for v in mem[22528:23296])
 screen(s.memory,ROOT/f'v3_ending_{kind}_{score}_{height}.png');key('EN');assert mem[S['mode']] in [6,7]
results['rocket_dancers_and_buran_endings']=True
s,t,mem=fresh();run(s,t,760);assert mem[S['demo']]==1 and mem[S['mode']]==1;key('q');assert mem[S['demo']]==0 and mem[S['mode']]==0;results['automatic_demo_and_cancel']=True
# Match original top-row exclusion and cap line counter.
s,t,mem=fresh();key('EN');mem[S['board']:S['board']+180]=[0x83]*10+[0]*170;call('clear_lines');assert mem[S['cleared']]==0
mem[S['board']:S['board']+180]=[0]*170+[0x83]*10;mem[S['lines']:S['lines']+2]=[15,39];mem[S['lines_bcd']:S['lines_bcd']+2]=[0x99,0x99];call('clear_lines');assert mem[S['lines']:S['lines']+2]==[15,39] and mem[S['lines_bcd']:S['lines_bcd']+2]==[0x99,0x99]
results['top_rows_and_9999_line_cap']=True
(ROOT/'validation_v3.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))

# Record ranking, mode/height/heart isolation, and reset keeping records in RAM.
s,t,mem=fresh()
for score in [0x10,0x20,0x15,0x05]:
 mem[S['score']:S['score']+3]=[score,0,0];call('check_record')
 if mem[S['mode']]==6:key('EN')
 run(s,t,20)
assert [mem[0x6000+i*9] for i in range(3)]==[0x20,0x15,0x10]
key('1');assert mem[S['mode']]==0 and mem[0x6000]==0x20
mem[S['gametype']]=1;mem[S['height']]=5;mem[S['startlevel']]=9;mem[S['heart']]=1
call('group_pointer');assert mem[S['record_group']]==139
results['ranked_records_separated_by_difficulty_and_reset']=True
# Fractional gravity agrees with elapsed original time within one Spectrum frame.
s,t,mem=fresh();key('EN')
original=[52,48,44,40,36,32,27,21,16,10,9,8,7,6,5,5,4,4,3,3,2]
for level,n in enumerate(original):
 mem[S['level']]=level;mem[0x703a]=0;total=0
 for _ in range(32):call('reset_gravity');total+=mem[S['falltimer']]
 assert abs(total-32*(n+1)*50/59.7275)<1.1,(level,total)
results['fractional_gravity_all_21_levels']=True
(ROOT/'validation_v3.json').write_text(json.dumps(results,indent=2));print('Additional checks: ranked records, reset and 21-level gravity passed')

# The original top-out counter allows one blocked lock at the spawn position.
s,t,mem=fresh();key('EN');mem[S['board']:S['board']+180]=[0]*180
for attempt in [1,2]:
 for name,val in [('mode',1),('piece',0),('rot',0),('px',3),('py',254)]:mem[S[name]]=val
 call('lock_piece')
 assert mem[0x7039]==attempt
 assert (mem[S['mode']]==3)==(attempt==2)
results['two_blocked_spawn_locks_top_out']=True
(ROOT/'validation_v3.json').write_text(json.dumps(results,indent=2));print('Two-lock top-out fixture passed')

# Compare the actual printed B subtotals with the original score formula.
s,t,mem=fresh();key('EN');mem[S['gametype']]=1;mem[S['level']]=3;mem[S['startlevel']]=3;mem[S['remaining']]=25
for rows in range(1,5):
 mem[S['board']:S['board']+180]=[0]*(180-rows*10)+[0x83]*(rows*10)
 call('clear_lines')
score_before=mem[S['score']:S['score']+3];call('show_b_summary');assert mem[S['score']:S['score']+3]==score_before
font=(ROOT/'assets/tiles.bin').read_bytes()
for row,text in [(6,'000160'),(8,'000400'),(10,'001200'),(12,'004800'),(17,'006560')]:
 col=18 if row==17 else 22
 for i,c in enumerate(text):
  expected=font[int(c)*8:int(c)*8+8]
  base=16384+((row*8&192)<<5)+((row*8&7)<<8)+((row*8&56)<<2)+col+i
  assert bytes(mem[base+y*256] for y in range(8))==expected,(row,text,c)
results['rendered_b_subtotals_match_original_formula']=True
# A complete B game, using keyboard input only.
from demo_player import DemoPlayer
s,t,mem=fresh();key('b');key('EN');ai=DemoPlayer()
for frame in range(10000):
 run(s,t,1,ai.keys(s.memory))
 if mem[S['mode']]!=1:break
run(s,t,40)
assert mem[S['mode']]==5,(frame,mem[S['mode']],mem[S['remaining']])
counts=[mem[S['stats']+i*2]+256*mem[S['stats']+i*2+1] for i in range(4)]
assert sum((i+1)*c for i,c in enumerate(counts))>=25
results['full_b_game_keyboard_only']={'frames':frame+1,'line_clear_counts':counts}
(ROOT/'validation_v3.json').write_text(json.dumps(results,indent=2));print('Rendered subtotals and a full B game passed:',results['full_b_game_keyboard_only'])
