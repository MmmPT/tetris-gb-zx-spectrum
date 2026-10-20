"""Read-only placement planning; the emulator receives keyboard input only."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];S=json.loads((ROOT/'symbols.json').read_text());SHAPES=json.loads((ROOT/'assets/shapes.json').read_text())
def valid(board,cells,x,y):
 return all(0<=x+dx<10 and y+dy<18 and (y+dy<0 or not board[(y+dy)*10+x+dx]) for dx,dy,_ in cells)
def choices(board,piece):
 seen=set()
 for r in range(4):
  cells=SHAPES[piece*4+r];pattern=tuple((x,y) for x,y,_ in cells)
  if pattern in seen:continue
  seen.add(pattern)
  for x in range(-3,10):
   y=-2
   if not valid(board,cells,x,y):continue
   while valid(board,cells,x,y+1):y+=1
   if any(y+dy<0 for dx,dy,_ in cells):continue
   b=board.copy()
   for dx,dy,tile in cells:b[(y+dy)*10+x+dx]=tile
   rows=[b[i:i+10] for i in range(0,180,10)];kept=[row for row in rows if not all(row)];clears=18-len(kept);b=[0]*(clears*10)+sum(kept,[])
   heights=[];holes=0
   for xx in range(10):
    top=18
    for yy in range(18):
     if b[yy*10+xx]:top=min(top,yy)
     elif top<18:holes+=1
    heights.append(18-top)
   score=clears*760-holes*360-sum(heights)*9-sum(abs(heights[i]-heights[i+1]) for i in range(9))*20-max(heights)*16
   yield score,r,x,b
class DemoPlayer:
 def __init__(self):self.id=-1;self.target=None;self.frame=0;self.plans=0;self.release=0
 def keys(self,m):
  self.frame+=1
  if m[S['mode']]!=1:return []
  identity=m[S['pieces']]+256*m[S['pieces']+1]
  if identity!=self.id:
   self.id=identity;self.plans+=1;self.release=2;board=[m[i] for i in range(S['board'],S['board']+180)];piece=m[S['piece']];nxt=m[S['next']];candidates=[]
   for score,r,x,b in choices(board,piece):
    future=max((v[0] for v in choices(b,nxt)),default=-10000)
    candidates.append((score+.55*future,r,x))
   if not candidates:self.target=(0,3)
   else:_,r,x=max(candidates);self.target=(r,x)
  if self.release:
   self.release-=1;return []
  r,x=self.target;rot=m[S['rot']];px=m[S['px']];px=px-256 if px>127 else px
  if rot!=r:return ['q'] if self.frame%4<2 else []
  if px!=x:return ['o' if px>x else 'p'] if self.frame%4<2 else []
  return ['a']
