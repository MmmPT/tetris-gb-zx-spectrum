from pathlib import Path
from PIL import Image
import numpy as np,re,json
ROOT=Path(__file__).resolve().parents[1];REF=ROOT/'reference/tetris-master';OUT=ROOT/'assets';OUT.mkdir(exist_ok=True)
text=(REF/'tetris.asm').read_text();sp=(REF/'sprites.asm').read_text()
def tiles_of(name):
 p=np.array(Image.open(REF/'gfx'/name).convert('L'));out=[]
 for y in range(0,p.shape[0],8):
  for x in range(0,p.shape[1],8):
   a=p[y:y+8,x:x+8];threshold=np.tile(np.array([[32,160],[224,96]]),(4,4));out.append((a<threshold).astype(np.uint8))
 return out
font=tiles_of('font.png');game=tiles_of('configandgameplay.png');title=tiles_of('copyrightandtitlescreen.png')
tiles=np.zeros((256,8,8),dtype=np.uint8)
for i,t in enumerate(font[:39]):tiles[i]=t
for i,t in enumerate(game):
 if i+0x30<256:tiles[i+0x30]=t
# Reproduce the original mixed 1bpp-font / 2bpp-copy transfer for tiles 27..2F.
font_bytes=b''.join(np.packbits(t,axis=1).tobytes() for t in font[:39])
original_title=np.asarray(Image.open(REF/'gfx/copyrightandtitlescreen.png').convert('L'))
title_bytes=bytearray()
for yy in range(0,len(original_title),8):
 for xx in range(0,original_title.shape[1],8):
  shade=(255-original_title[yy:yy+8,xx:xx+8])//85
  lo=np.packbits(shade&1,axis=1);hi=np.packbits((shade>>1)&1,axis=1)
  for row in range(8):title_bytes.extend([int(lo[row,0]),int(hi[row,0])])
transfer=(font_bytes+title_bytes)[39*8:39*8+160]
threshold=np.tile(np.array([[32,160],[224,96]]),(4,4))
for ident in range(39,48):
 chunk=np.asarray(list(transfer[(ident-39)*16:(ident-38)*16]),dtype=np.uint8).reshape(8,2)
 lo=np.unpackbits(chunk[:,0,None],axis=1);hi=np.unpackbits(chunk[:,1,None],axis=1)
 luma=255-(lo+hi*2)*85;tiles[ident]=(luma<threshold).astype(np.uint8)
tiles[0x2f]=0;tiles[255]=1

def table(label):
 section=text.split(label+'::',1)[1].split('\n\n',1)[0]
 return np.array([int(x,16) for x in re.findall(r'\$([0-9A-Fa-f]{2})',section)],dtype=int).reshape(18,20)
def scr(pixels,attrs):
 b=bytearray(6912)
 for y in range(192):
  a=((y&192)<<5)+((y&7)<<8)+((y&56)<<2);b[a:a+32]=np.packbits(pixels[y]).tobytes()
 b[6144:]=attrs.tobytes();return b
def char(ch):
 if ch.isdigit():return int(ch)
 if ch.isalpha():return ord(ch.upper())-65+10
 return {' ':0x2f,'-':0x25,'.':0x24}.get(ch,0x2f)
def putstr(p,y,x,s):
 for c in s:
  p[y*8:y*8+8,x*8:x*8+8]=tiles[char(c)];x+=1
def screen(label,library):
 p=np.zeros((192,256),dtype=np.uint8);attrs=np.full((24,32),7,dtype=np.uint8);attrs[3:21,6:26]=56
 for y,row in enumerate(table(label)):
  for x,t in enumerate(row):p[24+y*8:32+y*8,48+x*8:56+x*8]=library[t]
 # Outer captions are white ink on black, so invert native black-on-white glyphs.
 if label=='TitleScreenTilemap':
  putstr(p,0,2,'TETRIS  GAME BOY TO ZX 128K')
 return p,attrs
for label,out in [('TypeAGameplayTilemap','game_a'),('TypeBGameplayTilemap','game_b')]:
 p,a=screen(label,tiles)
 # Keep the original Game Boy tilemap, walls, shadows and panel backgrounds.
 (OUT/(out+'.scr')).write_bytes(scr(p,a))
 pimg=np.zeros_like(p);pimg[:]=p
 # Match black ink on white paper for preview.
 rgb=np.zeros((192,256),dtype=np.uint8)
 for y in range(192):
  for x in range(256):rgb[y,x]=255 if (p[y,x]==0 if a[y//8,x//8]==56 else p[y,x]) else 0
 Image.fromarray(rgb).resize((768,576),Image.Resampling.NEAREST).save(OUT/(out+'.png'))
lib=tiles.copy()
for i,t in enumerate(title):
 if i+39<256:lib[i+39]=t
lib[0x2f]=0
p,a=screen('TitleScreenTilemap',lib)
p[24+14*8:24+18*8,48:208]=0
for y,s in [(17,'A-TYPE  LEVEL 0'),(18,'O P LEVEL  MUSIC A'),(19,'B MODE  H HEIGHT'),(20,'ENTER START')]:putstr(p,y,7,s)
# Menu outer footer.
p[22*8:]=0;putstr(p,22,1,'QAOP OR KEMPSTON  K ON-OFF');putstr(p,23,1,'T MUSIC  L HEART  R RECORDS')
(OUT/'menu.scr').write_bytes(scr(p,a))
# Read the first 28 original 4x4 tile sprite matrices.
parts=[];forms=[]
for chunk in re.split(r'SpriteTiles_[0-9A-F]+::',sp)[1:29]:
 lines=[l.split(';')[0] for l in chunk.splitlines() if l.strip().startswith('db ')]
 vals=[int(v,16) for v in re.findall(r'\$([0-9A-F]{2})', '\n'.join(lines))]
 vals=vals[:vals.index(0xff)];vals+= [0xfe]*(16-len(vals));cells=[]
 for i,v in enumerate(vals):
  if v!=0xfe:cells.append((i%4,i//4,v))
 assert len(cells)==4,cells
 forms.append(cells);parts.extend([v for cell in cells for v in cell])
(OUT/'shapes.bin').write_bytes(bytes(parts));(OUT/'shapes.json').write_text(json.dumps(forms))
from music_assets import build
build()
print('Assets:',len(forms),'original rotations')

from sfx_assets import build as build_sfx
build_sfx()
def compress(data):
 out=bytearray();i=0
 def repeat(i):
  n=1
  while i+n<len(data) and n<128 and data[i+n]==data[i]:n+=1
  return n
 while i<len(data):
  n=repeat(i)
  if n>=3:out.extend([128+n-1,data[i]]);i+=n
  else:
   start=i;i+=n
   while i<len(data) and i-start<125 and repeat(i)<3:i+=repeat(i)
   out.append(i-start);out.extend(data[start:i])
 out.append(0);return out
for name in ['menu','game_a','game_b']:
 data=compress((OUT/(name+'.scr')).read_bytes());(OUT/(name+'.rle')).write_bytes(data);print(name,'compressed:',len(data))

from ui_assets import build as build_ui
build_ui()

# Preserve elapsed GB gravity times with a fractional 50 Hz schedule.
grav=[52,48,44,40,36,32,27,21,16,10,9,8,7,6,5,5,4,4,3,3,2]
values=[]
for n in grav:
 frames=(n+1)*50/59.7275;whole=int(frames);values.extend([whole,round((frames-whole)*256)])
(OUT/'gravity.bin').write_bytes(bytes(values))

# Apply the selected colour proposal to live piece tiles only, after rendering
# original backgrounds; decorative tiles in the SCR files retain the original art.
colour_block=np.unpackbits(np.array([255,129,129,129,129,129,129,255],dtype=np.uint8)).reshape(8,8)
for ident in [0x80,0x81,0x82,0x83,0x84,0x85,0x86,0x87,0x88,0x89,0x8a,0x8b,0x8f]:tiles[ident]=colour_block
(OUT/'tiles.bin').write_bytes(np.packbits(tiles,axis=2).tobytes())
