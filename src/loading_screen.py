"""Convert the loading illustration to a real 6912-byte Spectrum screen."""
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def build():
 im=Image.open(ROOT/'assets/loading_reference.png').convert('RGB').resize((256,192),Image.Resampling.LANCZOS)
 rgb=np.asarray(im,dtype=np.float32).reshape(24,8,32,8,3).transpose(0,2,1,3,4).reshape(768,64,3)
 candidates=[];palettes=[]
 for bright,v in [(1,255)]:
  pal=np.array([(v if c&2 else 0,v if c&4 else 0,v if c&1 else 0) for c in range(8)],dtype=np.float32)
  dist=((rgb[:,:,None,:]-pal[None,None,:,:])**2).sum(axis=-1)
  for paper in [0]:
   for ink in range(paper+1,8):
    candidates.append(np.minimum(dist[:,:,paper],dist[:,:,ink]).sum(axis=1))
    palettes.append((bright,paper,ink,pal))
 choices=np.argmin(np.stack(candidates),axis=0)
 pixels=np.zeros((192,256),dtype=np.uint8);attrs=np.zeros((24,32),dtype=np.uint8);preview=np.zeros((192,256,3),dtype=np.uint8)
 for cell,choice in enumerate(choices):
  bright,paper,ink,pal=palettes[choice];y,x=divmod(cell,32)
  patch=rgb[cell];bits=(((patch-pal[ink])**2).sum(axis=1)<((patch-pal[paper])**2).sum(axis=1)).reshape(8,8)
  pixels[y*8:y*8+8,x*8:x*8+8]=bits
  preview[y*8:y*8+8,x*8:x*8+8]=np.where(bits[:,:,None],pal[ink],pal[paper]).astype(np.uint8)
  attrs[y,x]=bright*64+paper*8+ink
 # Use native glyphs for the small footer instead of resampling artwork text.
 tiles=(ROOT/'assets/tiles.bin').read_bytes()
 pixels[176:192,64:192]=0;preview[176:192,64:192]=0;attrs[22:24,8:24]=71
 for index,ch in enumerate('ZX SPECTRUM 128K'):
  tile=int(ch) if ch.isdigit() else ord(ch)-65+10 if ch.isalpha() else 0x2f
  glyph=np.unpackbits(np.frombuffer(tiles[tile*8:tile*8+8],dtype=np.uint8)).reshape(8,8)
  x=64+index*8
  pixels[176:184,x:x+8]=glyph
  colour=(255,255,0) if index>=12 else (255,255,255)
  attrs[22,8+index]=70 if index>=12 else 71
  preview[176:184,x:x+8]=glyph[:,:,None]*np.array(colour,dtype=np.uint8)
 data=bytearray(6912)
 for y in range(192):
  a=((y&192)<<5)+((y&7)<<8)+((y&56)<<2);data[a:a+32]=np.packbits(pixels[y]).tobytes()
 data[6144:]=attrs.tobytes();assert len(data)==6912 and not(attrs&128).any()
 (ROOT/'assets/loading.scr').write_bytes(data)
 Image.fromarray(preview).resize((768,576),Image.Resampling.NEAREST).save(ROOT/'assets/loading_preview.png')
 print('Loading screen: 256x192, 6912 bytes, 2 colours per 8x8 cell, no FLASH')
if __name__=='__main__':build()
