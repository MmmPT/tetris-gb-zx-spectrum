from pathlib import Path
import re,json,subprocess
from skoolkit.z80 import Assembler
from loading_screen import build as build_loading
build_loading()
from skoolkit.snapshot import Snapshot,write_snapshot
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dist';OUT.mkdir(exist_ok=True)
variables={'heart':0x7036,'menu_t':0x7081,'menu_l':0x7082,'menu_r':0x7083,'result_done':0x7084,'name_pos':0x7085,'record_group':0x7086,'demo':0x7087,'idle':0x7088,'ending_time':0x708a,'ending_phase':0x708c,'ending_done':0x708d,'record_ptr':0x708e,'stats':0x7090,'soft_total':0x7098,'ui_row':0x709a,'name_buf':0x70a0,'song_index':0x7037,'music_choice':0x7038,'song_base':0x7068,'drum_ptr':0x706c,'drum_left':0x706e,'drum_age':0x706f,'drum_note':0x7070,'sfx_pending':0x7060,'sfx_priority':0x7061,'sfx_active':0x7062,'sfx_ptr':0x7063,'sfx_left':0x7065,'sfx_frame':0x7066,'mode':0x7000,'piece':0x7001,'rot':0x7002,'px':0x7003,'py':0x7004,'next':0x7005,'level':0x7006,'startlevel':0x7007,'score':0x7008,'lines':0x700b,'lines_bcd':0x700d,'keys':0x700f,'edge':0x7010,'repeat':0x7011,'lastdir':0x7012,'falltimer':0x7013,'softtimer':0x7014,'softcount':0x7015,'pieces':0x7016,'rng':0x7018,'noteleft':0x701a,'music_ptr':0x701b,'music_on':0x701d,'period':0x701e,'cx':0x7020,'cy':0x7021,'cr':0x7022,'cellx':0x7023,'temp_ptr':0x7024,'rowtemp':0x7026,'scanrow':0x7027,'writerow':0x7028,'cleared':0x7029,'flash':0x702a,'erase':0x702b,'tiletemp':0x702c,'framewait':0x702d,'history':0x702e,'hidden':0x702f,'gametype':0x7030,'height':0x7031,'remaining':0x7032,'menu_b':0x7033,'menu_h':0x7034,'board':0x7200,'softgate':0x7035}
ops=[]
source=(ROOT/'src/game.asm').read_text()
source=re.sub(r'INCLUDE (\S+)',lambda m:(ROOT/'src'/m[1]).read_text(),source)
for n,line in enumerate(source.splitlines(),1):
 line=line.split(';')[0].strip()
 if line:ops.append((n,line))
labels=variables.copy();asm=Assembler();start=0x8000

def resolve(op,pc,first=False):
 def sub(m):
  value=(pc+2 if op.startswith('JR ') or op.startswith('DJNZ ') else 0) if first else labels[m[1]]+int(m[2]or 0)
  return '$%04X'%(value&65535)
 return re.sub(r'@(\w+)([+-]\d+)?',sub,op)
def assemble(op,pc,first):
 if op=='ENDINGTABLE':return b''.join((labels.get('ending_data',0)+int(v)).to_bytes(2,'little') for v in (ROOT/'assets/ending_offsets.txt').read_text().split(','))
 if op=='MUSICTABLE':return b''.join((labels.get('music_data',0)+offset).to_bytes(2,'little') for m in json.loads((ROOT/'assets/music_meta.json').read_text()) for offset in m['offsets'])
 if op=='SFXTABLE':return b''.join((labels.get('sfx_data',0)+int(v)).to_bytes(2,'little') for v in (ROOT/'assets/sfx_offsets.txt').read_text().split(','))
 if op.startswith('INCBIN '):return (ROOT/'assets'/op.split()[1]).read_bytes()
 if op.startswith('DB '):return bytes(int(v.strip().replace('$','0x'),0) for v in op[3:].split(','))
 if op.startswith('DW '):return b''.join(int(v.strip().replace('$','0x'),0).to_bytes(2,'little') for v in resolve(op[3:],pc,first).split(','))
 b=asm.assemble(resolve(op,pc,first),pc)
 if not b:raise ValueError('Cannot assemble '+op)
 return bytes(b)
for first in [True,False]:
 pc=start;blob=bytearray()
 for n,op in ops:
  if op.endswith(':'):
   if first:
    if op[:-1] in labels:raise ValueError('Duplicate label '+op)
    labels[op[:-1]]=pc
   continue
  try:b=assemble(op,pc,first)
  except Exception as e:raise ValueError(f'Line {n}: {op}: {e}') from e
  pc+=len(b);blob.extend(b)
assert pc<0xff00,hex(pc)
(OUT/'Tetris_GB.bin').write_bytes(blob)
# Build a real tape loader, then fast-load it from a fresh Spectrum ROM to
# create a matching standalone snapshot with clean BASIC system variables.
from skoolkit.bin2tap import main as make_tap
from skoolkit.tap2sna import main as load_tap
make_tap(['-o','32768','-c','32767','-s','32768','-S',str(ROOT/'assets/loading.scr'),str(OUT/'Tetris_GB.bin'),str(OUT/'Tetris_GB.tap')])
load_tap(['--start','32768',str(OUT/'Tetris_GB.tap'),str(OUT/'Tetris_GB.z80')])
snap=Snapshot.get(str(OUT/'Tetris_GB.z80'))
ram=snap.ram();banks=[[0]*16384 for _ in range(8)]
banks[5]=ram[:16384];banks[2]=ram[16384:32768];banks[0]=ram[32768:]
write_snapshot(str(OUT/'Tetris_GB.z80'),banks,['PC=32768','SP=32766','IY=23610','I=63'],['iff=1','im=1','border=0','7ffd=16','fffd=0'],machine='128K')
(ROOT/'symbols.json').write_text(json.dumps(labels,indent=2))
print('Built',len(blob),'bytes; end',hex(pc))
