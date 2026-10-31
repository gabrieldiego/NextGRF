"""Original rail geometry rendered to company-colour pixel art at three zooms."""
import math
from pathlib import Path
from PIL import ImageDraw
from render import canvas, save_sheet

CELL = (64,48)
SHEET_ITEMS = 32
RAMPS = {'body':list(range(9,16)), 'roof':list(range(4,11)), 'frame':[1,2,3,4,5],
         'cc':list(range(198,206)), 'cc2':list(range(80,88)), 'wood':list(range(104,115)),
         'glass':[16,17,18,154,155], 'coal':[1,2,3,4], 'load':list(range(108,118))}


def mesh(p, loaded=False):
    faces = []
    length = 32*p['length']/8
    def face(points, material): faces.append((points,material))
    def box(x0,x1,y0,y1,z0,z1,material):
        v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
           (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
        for indices in [(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]:
            face([v[i] for i in indices],material)
    def tube(x,y0,y1,z,radius,material,axis='y'):
        rings=[]
        for q in [y0,y1]:
            rings.append([(x+radius*math.cos(i*math.tau/12),q,z+radius*math.sin(i*math.tau/12))
                          if axis=='y' else (q,x+radius*math.cos(i*math.tau/12),z+radius*math.sin(i*math.tau/12))
                          for i in range(12)])
        face(rings[0],material)
        face(list(reversed(rings[1])),material)
        for i in range(12): face([rings[0][i],rings[1][i],rings[1][(i+1)%12],rings[0][(i+1)%12]],material)
    def windows(y0,y1,z=7):
        for sign in [-1,1]:
            for y in range(round(y0),round(y1),3):
                box(sign*3.05,sign*3.05+.12,y,y+1.6,z,z+1.6,'glass')
    def roof(y0,y1,z=8):
        tube(0,y0,y1,z,3.25,'roof')
        box(-3.3,3.3,y0,y1,3,z,'body')
    def wheels():
        if p['track']=='MGLV':
            box(-3.5,3.5,-length*.43,length*.43,.5,3,'frame')
            return
        positions=[-length*.30,length*.30] if p['generation']<3 else [-length*.32,-length*.20,length*.20,length*.32]
        for y in positions:
            for side in [-1,1]:
                tube(y,side*2.6,side*3.2,1.7,1.65,'frame',axis='x')
                box(side*3.15,side*3.15+.15,y-.65,y+.65,1,2.1,'roof')
    wheels()
    box(-3,3,-length*.47,length*.47,2,3.2,'frame')
    box(-1,1,-length*.53,length*.53,2,2.7,'frame')
    if p['kind']=='engine':
        if p['propulsion']=='steam':
            tube(0,-length*.42,length*.13,5.5 if p['year']<1835 else 6,2.1 if p['year']<1835 else 2.9,'roof')
            box(-2,2,-length*.28,-length*.19,7,12,'frame')
            box(-2.5,2.5,-length*.30,-length*.17,11,12.5,'roof')
            if p['year']<1835:
                box(-3.2,3.2,length*.09,length*.38,3,4.2,'wood')
                for x in [-2.8,2.8]:box(x-.2,x+.2,length*.30,length*.34,4,8.5,'wood')
            else:
                box(-3.2,3.2,length*.09,length*.37,3,8.9,'cc')
                box(-3.6,3.6,length*.06,length*.40,8.9,10,'roof')
            for side in [-1,1]:
                if p['year']>=1835:box(side*3.21,side*3.21+.15,length*.14,length*.27,6,8,'glass')
                box(side*3.05,side*3.05+.15,-length*.38,length*.10,3.2,4,'cc2')
            if p['year']>=1850:
                box(-2.4,2.4,length*.31,length*.46,3,5.5,'coal')
        else:
            streamline=p['propulsion'] in ('monorail','maglev') or p['speed']>=200
            hood=p['propulsion']=='diesel' and not p['capacity']
            if streamline:
                roof(-length*.19,length*.40,6.5)
                face([(-3.3,-length*.19,8),(3.3,-length*.19,8),(1,-length*.51,5),(-1,-length*.51,5)],'roof')
                for side in [-1,1]:
                    face([(side*3.3,-length*.19,3),(side*3.3,-length*.19,8),(side,-length*.51,5),(side,-length*.51,3)],'cc')
                face([(-2.5,-length*.23,7.6),(2.5,-length*.23,7.6),(1.6,-length*.36,6.4),(-1.6,-length*.36,6.4)],'glass')
            elif hood:
                box(-2.4,2.4,-length*.44,length*.12,3,6.8,'cc')
                box(-3.2,3.2,length*.10,length*.36,3,9,'body')
                box(-3.5,3.5,length*.08,length*.38,9,9.8,'roof')
                windows(length*.14,length*.30,7)
            else:roof(-length*.43,length*.42,7.8)
            for side in [-1,1]:
                box(side*3.1,side*3.1+.15,-length*.44,length*.44,3,5,'cc')
                box(side*3.1,side*3.1+.15,-length*.44,length*.44,5,5.8,'cc2')
            if not hood and not streamline:
                windows(-length*.36,-length*.15)
                windows(length*.20,length*.39)
                box(-2.5,2.5,-length*.44,-length*.43,6,8.4,'glass')
            if p['capacity']: windows(-length*.10,length*.17)
            elif not streamline:
                for y in range(round(-length*.10),round(length*.18),2):
                    box(-2.7,2.7,y,y+.8,9.2,9.5,'frame')
            if p['propulsion']=='electric':
                for side in [-1,1]:
                    face([(side*.2,0,10),(side*2,1,12),(side*.2,2,14),(side*.2,0,10)],'frame')
                box(-2.5,2.5,1.7,2,13.5,14,'frame')
            if streamline:
                face([(-3,-length*.43,3),(3,-length*.43,3),(2,-length*.50,6),(-2,-length*.50,6)],'cc')
    else:
        family=p['family']; gen=p['generation']; wood=gen<=2
        material='wood' if wood else 'body'
        if family in ('passenger','mail','box','livestock','refrigerated','valuables'):
            roof(-length*.44,length*.44,6.2 if wood else 7.2)
            if family=='passenger':
                windows(-length*.36,length*.38,6 if wood else 7)
                if gen==8: windows(-length*.36,length*.38,4.5)
                if gen==3: box(-1.2,1.2,-length*.33,length*.33,10,11,'roof')
            elif family in ('mail','valuables'):
                windows(-length*.30,-length*.10,6.7)
                for side in [-1,1]: box(side*3.15,side*3.15+.15,-1,2,3.3,8,'cc2')
            elif family=='livestock':
                for y in range(round(-length*.4),round(length*.4),2):
                    for side in [-1,1]: box(side*3.15,side*3.15+.15,y,y+.6,4.5,8,'wood')
            else:
                for side in [-1,1]: box(side*3.15,side*3.15+.15,-2,2,3.4,8,'cc2')
            for side in [-1,1]: box(side*3.2,side*3.2+.15,-length*.43,length*.43,3,4.3,'wood' if wood else 'cc')
            if wood:
                for side in [-1,1]:
                    for y in range(round(-length*.4),round(length*.4),3):
                        box(side*3.2,side*3.2+.12,y,y+.5,3,8.4,'wood')
        elif family=='tank':
            if wood:
                for y in [-length*.24,length*.24]: tube(0,y-2,y+2,5.5,2.4,'wood')
            else:
                tube(0,-length*.40,length*.40,5.9,3.1,'body')
                for y in [-length*.26,length*.26]: box(-3.1,3.1,y-.5,y+.5,3.7,7,'cc')
                box(-.8,.8,-1,1,8.7,9.6,'frame')
        elif family=='flat':
            box(-3.3,3.3,-length*.44,length*.44,3,3.8,material)
            for y in [-length*.35,length*.35]:
                for side in [-1,1]:box(side*2.8,side*2.8+.4,y,y+.5,3.4,7,'cc')
            if loaded:
                for x in [-1.6,0,1.6]:tube(x,-length*.36,length*.36,4.5,.75,'load')
        elif family=='bulk':
            box(-3.3,3.3,-length*.44,length*.44,3,4,material)
            box(-3.4,-2.7,-length*.44,length*.44,3.5,7,material)
            box(2.7,3.4,-length*.44,length*.44,3.5,7,material)
            for y in [-length*.44,length*.42]:box(-3.4,3.4,y,y+.6,3.5,7,material)
            if loaded:
                box(-2.7,2.7,-length*.40,length*.40,4,6.7,'coal')
                face([(-2.7,-length*.40,6.7),(2.7,-length*.40,6.7),(0,0,8.2)],'coal')
                face([(-2.7,length*.40,6.7),(2.7,length*.40,6.7),(0,0,8.2)],'coal')
            for y in [-length*.32,0,length*.32]:
                for side in [-1,1]:box(side*3.4,side*3.4+.35,y,y+.7,3,7,'wood' if wood else 'cc2')
    return faces


def render(p,direction,zoom=1,loaded=False):
    image=canvas((CELL[0]*zoom,CELL[1]*zoom)); draw=ImageDraw.Draw(image)
    angle=direction*math.pi/4; ca,sa=math.cos(angle),math.sin(angle)
    faces=[([(ca*x-sa*y,sa*x+ca*y,z) for x,y,z in points],mat) for points,mat in mesh(p,loaded)]
    faces.sort(key=lambda f:sum(y+z*.58 for x,y,z in f[0])/len(f[0]))
    for points,mat in faces:
        a,b,c=points[:3];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        norm=math.sqrt(sum(x*x for x in n)) or 1
        light=max(0,min(1,.55+(-n[0]-n[1]+abs(n[2]))/norm*.20))
        color=RAMPS[mat][round(light*(len(RAMPS[mat])-1))]
        draw.polygon([(round((CELL[0]/2+x)*zoom),round((CELL[1]/2+y*.6-z)*zoom)) for x,y,z in points],fill=color)
    return image


def write_sheets(items,directory):
    directory=Path(directory);directory.mkdir(exist_ok=True,parents=True)
    for chunk,offset in enumerate(range(0,len(items),SHEET_ITEMS)):
        subset=items[offset:offset+SHEET_ITEMS]
        for zoom in (1,2,4):
            sheet=canvas((CELL[0]*8*zoom,CELL[1]*len(subset)*2*zoom))
            for row,p in enumerate(subset):
                for stage in (0,1):
                    for heading in range(8):
                        sheet.paste(render(p,heading,zoom,bool(stage)),(heading*CELL[0]*zoom,(row*2+stage)*CELL[1]*zoom))
            save_sheet(sheet,directory/f'rail-{chunk}-{zoom}x.png')
    for zoom in (1,2,4):
        (directory/f'rail-{zoom}x.png').unlink(missing_ok=True)
