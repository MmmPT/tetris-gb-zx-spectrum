"""AY arrangements of the original GB sound events; priority is independent of music."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build():
 def gb(n):return 131072/(2048-n)
 def tone(hz,frames,vol):return (max(1,round(1773450/(16*hz))),vol,56,0,frames)
 def noise(period,frames,vol):return (1,vol,42,period,frames)
 effects={
  1:[tone(1048,2,10),tone(1394,2,9)],
  2:[tone(1394,3,10)],
  3:[tone(gb(0x787),2,11)]+[tone(gb(0x780 if i%2==0 else 0x740),3,v) for i,v in enumerate([10,9,6,4,2])],
  4:[tone(gb(0x766),1,7),tone(650,1,5)],
  5:[noise(27,1,max(0,13-i)) for i in range(15)],
  6:[tone(gb(0x400),5,14)]+[tone(gb(0x600+n),5,v) for n,v in zip([0,0x23,0x43,0x63,0x83,0xa3,0xc3,0xd3,0xe3,0xff],[9,8,7,6,5,4,3,2,1,1])],
  7:[tone(gb(0x7c1),3,14),tone(gb(0x7ac),6,13),tone(gb(0x7c1),3,13),tone(gb(0x7ac),8,12)]+[tone(1500-i*80,1,max(1,12-i)) for i in range(12)],
  8:[tone(hz,6,14) for hz in [1760,2217,2637,3520,1760]],
  9:[noise(31,2,max(0,15-i)) for i in range(14)],
  10:[tone(hz,7,12) for hz in [1048,1394,1048,1394]],
  11:[tone(157+i%3*4,1,max(1,14-i//4)) for i in range(40)],
  12:[tone(hz,5,12) for hz in [659,880,1048,1318]],
 }
 priorities=[0,1,2,2,1,3,6,8,9,4,10,11,10]
 data=bytearray();offsets=[]
 for ident in range(1,13):
  offsets.append(len(data))
  for period,volume,mixer,n,frames in effects[ident]:data.extend([period&255,period>>8,volume,mixer,n,frames])
  data.extend([0]*6)
 (ROOT/'assets/sfx.bin').write_bytes(data)
 (ROOT/'assets/sfx_offsets.txt').write_text(','.join(map(str,offsets)))
 (ROOT/'assets/sfx_priority.bin').write_bytes(bytes(priorities))
 print('AY effects:',len(effects),'bytes:',len(data))
if __name__=='__main__':build()
