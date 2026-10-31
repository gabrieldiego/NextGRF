"""Complete DEFAULT/NEXTGRF rail and surface comparison catalogs."""
import json
import textwrap
from PIL import Image, ImageDraw
from pdf import PDF
from reference import ROOT
from roster import DIRECTIONS, RELEASE
from rail import trains, GENERATIONS
from rail_render import render as rail_sprite
from rail_defaults import default_trains
from surface import surface_vehicles, ROAD_GENERATIONS
from surface_render import render as surface_sprite
from surface_defaults import default_surface

COLORS={'DEFAULT':(.16,.32,.55),'NEXTGRF':(.07,.40,.32)}
EXCLUDE={'sprites','loaded_sprites','source','name','key','role','shape','hull_length','image_index'}


def describe(value):
 if value is None:return 'Never expires'
 if isinstance(value,list):return ', '.join(map(str,value)) or 'None'
 if isinstance(value,float):return f'{value:.3f}'.rstrip('0').rstrip('.')
 return str(value)


def prepare(defaults, additions, renderer):
 for p in additions:
  p['source']='NEXTGRF'
  p['sprites']=[renderer(p,d,4) for d in range(8)]
  p['loaded_sprites']=[renderer(p,d,4,True) for d in range(8)]
 return sorted(defaults+additions,key=lambda p:(p['year'],p.get('feature','RAIL'),p['source'],p['name']))


def sprite_panel(pdf,sprites,y,label):
 pdf.text(36,y,label,8,True)
 for d,s in enumerate(sprites):
  x=36+d*65.5;rgba=s.convert('RGBA');box=rgba.getchannel('A').getbbox()
  pdf.rect(x,y+7,63,77,(.937,.953,.969))
  if box:
   crop=rgba.crop(box);factor=min(59/crop.width,59/crop.height)
   w,h=crop.width*factor,crop.height*factor
   pdf.image(crop,x+(63-w)/2,y+10+(59-h)/2,w,h)
  pdf.text(x+25,y+78,DIRECTIONS[d],7,True)


def catalog(category,items):
 pdf=PDF(f'NextGRF - Default and Extended {category} Catalog',category)
 pdf.page();pdf.rect(0,0,595,226,(.07,.12,.20))
 pdf.text(36,78,'NextGRF',40,True,(1,1,1));pdf.text(36,120,f'{category.upper()} CATALOG',24,True,(.48,.78,.91))
 default_count=sum(p['source']=='DEFAULT' for p in items)
 pdf.text(36,162,f'v{RELEASE} | {default_count} DEFAULT + {len(items)-default_count} NEXTGRF vehicles',12,color=(1,1,1))
 y=265
 paragraphs=[
  'Every original default vehicle and every addition is labeled DEFAULT or NEXTGRF. Entries are ordered by introduction year. Default sprites are extracted from OpenGFX2 Classic 0.8.1 for comparison only; the playable package contains original NextGRF art.',
  'Each entry shows eight headings, empty and loaded sprite stages, and the extracted or configured gameplay properties. Vehicles without external loads use the same appearance in both stages. Images are enlarged to fit each panel, not shown at a shared physical scale.',
  'Dates are base introduction dates; OpenTTD can add up to 511 days and a preview period. Capacity is in native units of the selected cargo, with a literal capacity callback for NextGRF wagons, ships and road vehicles. Passenger ferries refit between passengers and mail; they have one cargo compartment.',
  'Speeds are km/h and weights are empty metric tonnes. NextGRF values are requested values; engine encoding can round them. Power is horsepower. Purchase and running costs are raw factors; currency, inflation, difficulty and other NewGRFs determine actual prices. Model life is the purchase window, while vehicle life governs ageing of purchased vehicles.',
  'NextGRF supports Temperate, Arctic and Tropical climates. Livestock vehicles are limited to climates with livestock. Toyland defaults are included for completeness; no Toyland additions are made. Default rail and surface vehicles are unchanged. Default aircraft receive range-only changes, covered in the aircraft catalog. OpenTTD source is unchanged.',
  'Rail wagons have fixed generation IDs. Buying a newer generation increases capacity and speed; existing wagons do not silently upgrade. Use the game setting Wagon speed limits to enforce their speed limits. Ordinary rail wagons work on electrified rail; monorail and maglev use their separate wagon fleets.',
  'Sailing, electric, hybrid and future propulsion are visual and economic themes using standard vehicle mechanics. There is no wind, battery or fuel simulation. Cargo bodies distinguish dry cargo, liquids, livestock and refrigerated traffic. Ships have lower canal speed fractions where configured.',
  'Shared NextGRF rail/surface settings: free refits, primary and secondary company colours, zero excluded cargo classes, and no overrides. Trains use air drag 0.08, single heads, no wagon power, and normal smoke effects by engine class. Roads use ROAD, adhesion 0.30 and air drag 0.08. Ships are refittable. Complete NML, JSON data and source accompany these catalogs.',
 ]
 for paragraph in paragraphs:y=pdf.paragraph(36,y,paragraph,size=10,leading=14)+13
 pdf.end_page()
 if category=='Rail':
  pdf.page();pdf.text(36,58,'Wagon generations',25,True)
  pdf.paragraph(36,88,'Conventional rail reference capacities and speed limits. Mail shares the passenger speed limit. Monorail and maglev variants retain generation capacities with higher speed limits appropriate to their track.',size=10)
  pdf.text(36,159,'GEN  YEAR    PAX    MAIL    BULK    PAX km/h    FREIGHT km/h',10,True,mono=True)
  for i,(g,year,pax,mail,bulk,ps,fs,tare,length) in enumerate(GENERATIONS):pdf.text(36,190+i*30,f'{g:>2}   {year}    {pax:>3}    {mail:>3}     {bulk:>3}       {ps:>3}           {fs:>3}',10,mono=True)
  y=467
  for paragraph in ['Families: passenger coaches, mail vans, bulk wagons, covered vans, tankers, flat wagons, livestock vans, refrigerated vans and secure vans. Refrigerated rail vans begin in Generation 3. Livestock and secure capacities are three quarters of the bulk reference.',
   'Monorail G6/G7/G8 passenger limits: 360/420/480 km/h; freight: 180/210/240. Maglev G7/G8 passenger limits: 660/720 km/h; freight: 280/320. Monorail wagons begin in 1998; maglev wagons begin in 2020 so default locomotives can use them.',
   'Earlier generations stay on sale for an overlap period, then retire from the purchase list. Generation 8 and endgame locomotives remain available. Existing stock retains its original capacity, speed and appearance throughout its service life.']:
   y=pdf.paragraph(36,y,paragraph,size=11,leading=16)+18
  pdf.end_page()
 else:
  pdf.page();pdf.text(36,58,'Road cargo generations',25,True)
  pdf.text(36,105,'GEN  YEAR   km/h   CAPACITY   HP   EMPTY t',11,True,mono=True)
  for i,(g,year,speed,capacity,weight,power) in enumerate(ROAD_GENERATIONS):pdf.text(36,140+i*31,f'{g:>2}   {year}   {speed:>3}      {capacity:>3}     {power:>3}    {weight:>2}',11,mono=True)
  pdf.paragraph(36,430,'Seven cargo bodies: covered van, bulk truck, tanker, flatbed, livestock van, refrigerated van and secure van. Refrigerated trucks begin in Generation 2. Buses have their own 1886-2050 progression, from 12 passengers to 150-passenger double-deck vehicles and fast electric coaches.',size=11,leading=17)
  pdf.paragraph(36,535,'Shipping starts in 1700 with sailing passenger vessels, expands to sailing cargo ships, paddle steamers, liners and tankers, then container ships and faster ferries. The 2050 fleet offers both very large freight capacity and high-speed passenger service.',size=11,leading=17)
  pdf.end_page()
 first_entry=2+(len(items)+29)//30
 for offset in range(0,len(items),30):
  pdf.page();pdf.text(36,57,f'{category} fleet index',24,True)
  pdf.text(36,82,'YEAR / ORIGIN / VEHICLE / ENTRY PAGE',9,True)
  for i,p in enumerate(items[offset:offset+30]):
   y=108+i*22;pdf.text(36,y,p['year'],9);pdf.text(74,y,p['source'],8,True,COLORS[p['source']]);pdf.text(135,y,p['name'],9);pdf.text(530,y,first_entry+offset+i+1,8)
  pdf.end_page()
 for p in items:
  pdf.page();color=COLORS[p['source']];pdf.rect(36,30,80,21,color);pdf.text(43,45,p['source'],10,True,(1,1,1))
  pdf.text(130,45,f"{p['year']} | {p.get('feature',p.get('track','RAIL'))} | ID {p['id']}",10,True)
  pdf.text(36,80,p['name'],21,True);pdf.text(36,102,p.get('role','Original default vehicle'),10)
  sprite_panel(pdf,p['sprites'],124,'EMPTY / PURCHASE APPEARANCE')
  if 'loaded_sprites' in p:sprite_panel(pdf,p['loaded_sprites'],221,'LOADED APPEARANCE')
  fields=[(k,v) for k,v in p.items() if k not in EXCLUDE]
  # Render both columns sequentially, balancing wrapped line counts.
  columns=[[],[]];heights=[0,0]
  for key,value in fields:
   lines=textwrap.wrap(f"{key}: {describe(value)}",width=53,break_long_words=False) or ['']
   col=0 if heights[0]<=heights[1] else 1;columns[col].append(lines);heights[col]+=len(lines)+.40
  for col,entries in enumerate(columns):
   x=36+col*267;y=341
   for lines in entries:
    for line in lines:pdf.text(x,y,line,8.2);y+=11
    y+=4.4
   if y>797:raise ValueError(f'Catalog properties overflow: {p["name"]}: {y}')
  pdf.end_page()
 path=ROOT/f'build/NextGRF-{category}-Catalog.pdf';pdf.save(path)
 data=[{k:v for k,v in p.items() if k not in ('sprites','loaded_sprites')} for p in items]
 (ROOT/f'build/{category.lower()}-catalog-data.json').write_text(json.dumps(data,indent=2)+'\n')
 # Compact reviewer contact sheet of all additions.
 own=[p for p in items if p['source']=='NEXTGRF'];preview=Image.new('RGB',(1000,((len(own)+3)//4)*130),'#eff3f7');draw=ImageDraw.Draw(preview)
 for i,p in enumerate(own):
  x=(i%4)*250;y=(i//4)*130;s=p.get('loaded_sprites',p['sprites'])[1].convert('RGBA');s=s.crop(s.getbbox());s.thumbnail((230,94))
  preview.paste(s,(x+(250-s.width)//2,y+24+(94-s.height)//2),s);draw.text((x+5,y+5),f"{p['year']} {p['name']}",fill='#17344d')
 preview.save(ROOT/f'build/{category.lower()}-preview.png')
 print(f'{path}: {len(pdf.pages)} pages, {len(items)} entries')


def main():
 catalog('Rail',prepare(default_trains(),trains(),rail_sprite))
 catalog('Surface',prepare(default_surface(),surface_vehicles(),surface_sprite))


if __name__=='__main__':main()
