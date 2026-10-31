"""Editable original ship and road-vehicle meshes, including sail-era vessels."""
import math
from pathlib import Path
from PIL import ImageDraw
from render import canvas, save_sheet
from rail_render import RAMPS

CELLS={'SHIP':(160,160),'ROADVEH':(64,48)}
SHEET_ITEMS=8


class Mesh:
 def __init__(self):self.faces=[]
 def face(self,points,material):self.faces.append((points,material))
 def box(self,x0,x1,y0,y1,z0,z1,mat):
  v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
  for ids in [(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]:self.face([v[i] for i in ids],mat)
 def tube(self,x,y0,y1,z,r,mat):
  rings=[[(x+r*math.cos(i*math.tau/12),y,z+r*math.sin(i*math.tau/12)) for i in range(12)] for y in [y0,y1]]
  self.face(rings[0],mat);self.face(list(reversed(rings[1])),mat)
  for i in range(12):self.face([rings[0][i],rings[1][i],rings[1][(i+1)%12],rings[0][(i+1)%12]],mat)


def mesh(p,loaded=False):
 m=Mesh()
 if p['feature']=='SHIP':
  length=p['hull_length'];beam=length*.16
  plan=[(0,-length*.50),(-beam*.70,-length*.37),(-beam,-length*.12),(-beam,length*.38),
        (-beam*.65,length*.48),(beam*.65,length*.48),(beam,length*.38),(beam,-length*.12),(beam*.70,-length*.37)]
  m.face([(x,y,4) for x,y in plan],'wood' if p['year']<1850 else 'body')
  for a,b in zip(plan,plan[1:]+plan[:1]):
   m.face([(a[0],a[1],4),(b[0],b[1],4),(b[0]*.72,b[1]*.94,0),(a[0]*.72,a[1]*.94,0)],'cc')
   m.face([(a[0],a[1],4),(b[0],b[1],4),(b[0],b[1],5),(a[0],a[1],5)],'cc2')
  shape=p['shape']
  if shape in ('sail','brig','clipper'):
   for yy in ([0] if p['key']=='mps_sloop' else [-length*.18,length*.18] if shape!='clipper' else [-length*.24,0,length*.25]):
    height=length*.70
    m.box(-.55,.55,yy-.55,yy+.55,4,height,'wood')
    for h,factor in [(height*.50,1),(height*.78,.78)]:
     width=beam*1.15*factor
     m.box(-width,width,yy-.3,yy+.3,h,h+.5,'wood')
     m.face([(-width,yy,h),(width,yy,h),(width*.76,yy+2,h-height*.22),(-width*.76,yy+2,h-height*.22)],'body')
    m.face([(0,yy,height),(beam*.6,yy,height-1),(0,yy,height-3)],'cc2')
   m.box(-beam*.6,beam*.6,length*.27,length*.40,4,8,'wood')
   if loaded and p['family']=='cargo':m.box(-beam*.65,beam*.65,-length*.1,length*.15,4,7,'load')
  elif p['family']=='tanker':
   for xx in [-beam*.45,beam*.45]:m.tube(xx,-length*.30,length*.20,6,beam*.3,'body')
   m.box(-beam*.55,beam*.55,length*.28,length*.40,4,12,'body')
   m.box(-beam*.65,beam*.65,length*.26,length*.40,9,10,'cc2')
  elif shape=='container':
   m.box(-beam*.7,beam*.7,length*.27,length*.42,4,15,'body')
   m.box(-beam*.75,beam*.75,length*.25,length*.43,11,13,'glass')
   if loaded:
    for row in range(3):
     for column in [-1,0,1]:
      x=column*beam*.55;y=-length*.28+row*length*.15
      m.box(x-beam*.24,x+beam*.24,y,y+length*.12,4,10+3*(row%2),'cc2' if (row+column)%2 else 'cc')
   else:m.box(-beam*.75,beam*.75,-length*.30,length*.18,4,5,'roof')
  elif p['family']=='ferry':
   m.box(-beam*.74,beam*.74,-length*.28,length*.32,4,9,'body')
   if p['capacity']>200:m.box(-beam*.64,beam*.64,-length*.18,length*.26,9,13,'body')
   for yy in range(round(-length*.25),round(length*.30),4):
    for side in [-1,1]:m.box(side*beam*.75,side*beam*.75+.25,yy,yy+2,6,8,'glass')
   m.box(-beam*.75,beam*.75,-length*.30,-length*.26,7,9,'glass')
   if shape in ('paddle','liner'):
    for yy in [0,length*.15] if shape=='liner' else [length*.1]:m.box(-2,2,yy,yy+3,9,17,'cc2')
   if shape=='paddle':
    for side in [-1,1]:m.box(side*(beam+2)-1.2,side*(beam+2)+1.2,-4,4,2,8,'wood')
   if shape in ('catamaran','hydrofoil'):
    for side in [-1,1]:m.box(side*(beam+2)-1,side*(beam+2)+1,-length*.30,length*.35,-1,2,'cc')
  else:
   m.box(-beam*.68,beam*.68,length*.18,length*.38,4,12,'body')
   m.box(-2,2,length*.12,length*.18,10,18,'cc2')
   m.box(-beam*.75,beam*.75,-length*.30,length*.05,4,7 if loaded else 5,'coal' if loaded else 'roof')
 else:
  length=30*p['length']/8;front=-length*.46;rear=length*.45
  m.box(-3.3,3.3,front,rear,2,3,'frame')
  for yy in [front+3,rear-3]+([rear-7] if p['year']>=1975 else []):
   for side in [-1,1]:
    m.box(side*3.1-.6,side*3.1+.6,yy-1.4,yy+1.4,.3,3,'frame')
    m.box(side*3.2-.2,side*3.2+.2,yy-.6,yy+.6,1,2,'roof')
  if p['family']=='bus':
   top=12 if p['shape']=='doubledeck' else 8
   m.box(-3.3,3.3,front,rear,3,top,'body')
   for yy in range(round(front+2),round(rear-1),3):
    for side in [-1,1]:
     m.box(side*3.3,side*3.3+.2,yy,yy+1.7,5.6,7.3,'glass')
     if top==12:m.box(side*3.3,side*3.3+.2,yy,yy+1.7,9,10.7,'glass')
   m.box(-3,3,front-.1,front+.1,5.5,7.5,'glass')
   for side in [-1,1]:m.box(side*3.3,side*3.3+.2,front,rear,3.1,4.5,'cc')
   m.box(-3.4,3.4,front,rear,top,top+.7,'cc2')
   if p['year']<1900:m.box(-.6,.6,front+3,front+4,8,11,'frame')
  else:
   cab_end=front+length*.30
   m.box(-3.2,3.2,front,cab_end,3,7.8,'cc')
   m.box(-2.8,2.8,front-.1,front+.1,5.8,7.1,'glass')
   for side in [-1,1]:m.box(side*3.2,side*3.2+.2,front+1,cab_end-1,5.7,7.3,'glass')
   family=p['family'];body_start=cab_end+1
   if family=='tank':m.tube(0,body_start,rear,6,3,'body')
   elif family in ('box','refrigerated','valuables','livestock'):
    m.box(-3.4,3.4,body_start,rear,3,9,'wood' if p['year']<1935 else 'body')
    m.box(-3.5,3.5,body_start,rear,8.8,9.3,'cc2')
    if family=='livestock':
     for yy in range(round(body_start),round(rear),2):
      for side in [-1,1]:m.box(side*3.5,side*3.5+.15,yy,yy+.6,4,8,'roof')
   elif family=='bulk':
    m.box(-3.4,3.4,body_start,rear,3,6,'cc2')
    m.box(-2.8,2.8,body_start+.5,rear-.5,5.8,7 if loaded else 6,'coal' if loaded else 'roof')
   else:
    m.box(-3.4,3.4,body_start,rear,3,3.7,'wood')
    if loaded:
     for xx in [-1.6,0,1.6]:m.tube(xx,body_start+.5,rear-.5,4.5,.8,'load')
  for xx in [-2.3,2.3]:m.box(xx-.4,xx+.4,front-.3,front,3.8,4.5,'body')
 return m.faces


def render(p,direction,zoom=1,loaded=False):
 cell=CELLS[p['feature']];image=canvas((cell[0]*zoom,cell[1]*zoom));draw=ImageDraw.Draw(image)
 a=direction*math.pi/4;ca,sa=math.cos(a),math.sin(a)
 faces=[([(ca*x-sa*y,sa*x+ca*y,z) for x,y,z in points],mat) for points,mat in mesh(p,loaded)]
 faces.sort(key=lambda f:sum(y+z*.58 for x,y,z in f[0])/len(f[0]))
 for points,mat in faces:
  a,b,c=points[:3];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
  n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);norm=math.sqrt(sum(x*x for x in n)) or 1
  light=max(0,min(1,.55+(-n[0]-n[1]+abs(n[2]))/norm*.20));color=RAMPS[mat][round(light*(len(RAMPS[mat])-1))]
  draw.polygon([(round((cell[0]/2+x)*zoom),round((cell[1]/2+y*.6-z)*zoom)) for x,y,z in points],fill=color)
 return image


def write_sheets(items,directory):
 directory=Path(directory);directory.mkdir(exist_ok=True,parents=True)
 for feature in CELLS:
  subset=[p for p in items if p['feature']==feature];cell=CELLS[feature]
  for chunk,offset in enumerate(range(0,len(subset),SHEET_ITEMS)):
   group=subset[offset:offset+SHEET_ITEMS]
   for zoom in [1,2,4]:
    sheet=canvas((cell[0]*8*zoom,cell[1]*len(group)*2*zoom))
    for row,p in enumerate(group):
     for stage in [0,1]:
      for d in range(8):sheet.paste(render(p,d,zoom,bool(stage)),(d*cell[0]*zoom,(row*2+stage)*cell[1]*zoom))
    save_sheet(sheet,directory/f'{feature.lower()}-{chunk}-{zoom}x.png')
