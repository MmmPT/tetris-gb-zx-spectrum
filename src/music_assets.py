"""Convert original pitched and percussion sequences into compact AY streams."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
def build():
 text=(ROOT/'reference/tetris-master/music.asm').read_text();sections=dict(re.findall(r'(\w+)::\n(.*?)(?=\n\w+::|\Z)',text,re.S))
 names={'C_':1,'C#':2,'D_':3,'D#':4,'E_':5,'F_':6,'F#':7,'G_':8,'G#':9,'A_':10,'A#':11,'B_':12}
 songs=['6F6B','6F76','6F81','6F55','6F60','6F4A','6F3F','6FA2','6FAD','6FB8','6FC3','6FCE','6FD9','6FE4']
 tempos={'6F2B':[4,9,18,36,72,144,27,54,108,12,24], '6F0E':[3,6,12,24,48,96,18,36,72,8,16,0], '6F05':[3,5,10,20,40,80,15,30,60], '6EF9':[2,4,8,16,32,64,12,24,48,5,0,1]}
 blob=bytearray();dedup={};meta=[]
 def stream(channel,lengths,noise=False):
  events=[];duration=lengths[2]
  for section in re.findall(r'Section_\w+',sections.get(channel,'')):
   for line in sections[section].splitlines():
    line=line.strip()
    if re.fullmatch(r'db \$A[0-9A-B]',line):duration=lengths[int(line[-1],16)]
    elif line.startswith('Notes ') and not noise:
     v=[v.strip() for v in line[6:].split(',')]
     for i in range(0,len(v),2):
      encoded=names[v[i]]+(int(v[i+1])-2)*12;assert encoded%2==0
      midi=36+encoded//2-1;freq=440*2**((midi-69)/12);events.append((max(1,round(1773450/(16*freq))),duration))
    elif line.startswith('Noise ') and noise:
     events.extend([(int(v)+1,duration) for v in line[6:].split(',')])
    elif line=='Rest':events.append((0,duration))
  if not events:events=[(0,255)]
  t=last=0;data=[]
  for note,d in events:
   t+=d;end=round(t*50/59.7275);n=max(1,end-last);last=end
   while n>255:
    data.extend([note,255] if noise else [note&255,note>>8,255]);n-=255
   data.extend([note,n] if noise else [note&255,note>>8,n])
  data.extend([0,0] if noise else [0,0,0]);return bytes(data),{'notes':len(events),'frames':last}
 for idx,song in enumerate(songs):
  words=re.findall(r'dw ([^\n]+)',sections['Song_'+song]);tempo=words[0].strip().lstrip('$');channels=[w.strip() for w in words[1:]]
  # Game Boy square 2 carries the lead; square 1 is the borrowed effect/harmony voice.
  channels=[channels[1],channels[0],channels[2],channels[3]];info={'song':song,'offsets':[],'voices':[],'loop':int(idx in [0,1,2,3,6])}
  for v,ch in enumerate(channels):
   data,report=stream(ch,tempos[tempo],v==3)
   if data not in dedup:dedup[data]=len(blob);blob.extend(data)
   info['offsets'].append(dedup[data]);info['voices'].append(report)
   if idx==0 and v<3:(ROOT/f'assets/music_{"abc"[v]}.bin').write_bytes(data)
  meta.append(info)
 (ROOT/'assets/music_all.bin').write_bytes(blob);(ROOT/'assets/music_meta.json').write_text(json.dumps(meta,indent=2));(ROOT/'assets/music_loops.bin').write_bytes(bytes(m['loop'] for m in meta));(ROOT/'music_validation.json').write_text(json.dumps(meta,indent=2))
 print('Original music:',len(meta),'songs;',len(blob),'bytes')
if __name__=='__main__':build()
