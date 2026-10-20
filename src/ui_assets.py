"""Original ending sprites rendered from the GB matrices into native 1-bit stamps."""
from pathlib import Path
import re,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];REF=ROOT/'reference/tetris-master'
def build():
 text=(REF/'tetris.asm').read_text();sp=(REF/'sprites.asm').read_text();sections=dict(re.findall(r'(\w+)::\n(.*?)(?=\n\w+::|\Z)',sp,re.S))
 def tiles(name):
  p=np.array(Image.open(REF/'gfx'/name).convert('L'));out=[]
  for y in range(0,len(p),8):
   for x in range(0,p.shape[1],8):out.append((p[y:y+8,x:x+8]<np.tile([[32,160],[224,96]],(4,4))).astype(np.uint8))
  return out
 game=[np.zeros((8,8),dtype=np.uint8)]*48+tiles('configandgameplay.png');rocket=tiles('multiplayerandburan.png')
 addresses=[int(x,16) for x in re.findall(r'\$([0-9A-Fa-f]{4})',text.split('SpriteList::',1)[1].split('SECTION',1)[0])]
 def sprite(index,library):
  header=sections['Sprite_%04X'%addresses[index]];name=re.search(r'dw (\w+)',header)[1];part=sections[name];matrix=re.search(r'dw (\w+)',part)[1]
  m=text.split(matrix+'::',1)[1].split('\n\n',1)[0];coords=[int(x,16) for x in re.findall(r'\$([0-9A-F]{2})',m)];coords=list(zip(coords[::2],coords[1::2]));v=[int(x,16) for x in re.findall(r'\$([0-9A-F]{2})',part.split('\n',1)[1])]
  p=np.zeros((64,64),dtype=np.uint8);i=0;cell=0;maxx=maxy=0
  while i<len(v) and v[i]!=255:
   tile=v[i];i+=1;flip=False
   if tile==253:flip=True;tile=v[i];i+=1
   y,x=coords[cell];cell+=1;maxx=max(maxx,x+8);maxy=max(maxy,y+8)
   if tile==254:continue
   t=library[tile] if tile<len(library) else np.zeros((8,8),dtype=np.uint8)
   p[y:y+8,x:x+8]=t[:,::-1] if flip else t
  p=p[:maxy,:maxx];data=bytearray([maxx//8,maxy//8])
  for y in range(0,maxy,8):
   for x in range(0,maxx,8):data.extend(np.packbits(p[y:y+8,x:x+8],axis=1).tobytes())
  return bytes(data)
 ids=[0x44,0x46,0x48,0x4a,0x4c,0x4e,0x50,0x52,0x54,0x55]
 data=bytearray();offsets=[]
 for phase in range(2):
  for ident in ids:offsets.append(len(data));data.extend(sprite((ident+phase if ident<0x54 else ident^phase),game))
 for ident in [0x58,0x59,0x5a,0x2c]:offsets.append(len(data));data.extend(sprite(ident,rocket))
 (ROOT/'assets/ending_stamps.bin').write_bytes(data);(ROOT/'assets/ending_offsets.txt').write_text(','.join(map(str,offsets)));print('Original ending stamps:',len(data),'bytes')
if __name__=='__main__':build()
