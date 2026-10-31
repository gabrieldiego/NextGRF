"""Extract the untouched 88 road vehicles and 11 ships for comparison."""
import configparser
import datetime
import re
from defaults import GRF, REPO
from reference import ensure_reference


def default_surface(graphics=True):
 text=(REPO/'src/table/engines.h').read_text();info={}
 for m in re.finditer(r'\b(MR|MS)\(\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),(.*?)//\s*(\d+) (.+)',text):
  kind,days,decay,life,model,tail,identifier,name=m.groups()
  inside=tail.split('LandscapeTypes({',1)[1].split('}',1)[0]
  date=datetime.date(1920,1,1)+datetime.timedelta(days=int(days))
  info[int(identifier)]=dict(year=date.year,introduction_date=str(date),climates=[n for t,n in [('T','TEMPERATE'),('A','ARCTIC'),('S','TROPICAL'),('Y','TOYLAND')] if t in inside],
    reliability_decay=int(decay),vehicle_life=int(life),model_life=int(model),default_cargo=tail.split(',')[0].strip())
 files={};mapping={};arrays={}
 if graphics:
  gfx=ensure_reference();manifest=configparser.ConfigParser();manifest.read(next(gfx.glob('*.obg')))
  for key in ['base','arctic','tropical','toyland']:files[key]=GRF(gfx/manifest['files'][key])
  landscape=(REPO/'src/table/landscape_sprite.h').read_text()
  for key,token in [('arctic','arctic'),('tropical','tropic'),('toyland','toyland')]:
   body=landscape.split(f'_landscape_spriteindexes_{token}[] = {{',1)[1].split('};',1)[0];offset=0;table={}
   for a,b in re.findall(r'\{\s*(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+)\}',body):
    for sprite in range(int(a,16),int(b,16)+1):table[sprite]=offset;offset+=1
   mapping[key]=table
  for feature,filename,name in [('SHIP','ship_cmd.cpp','_ship_sprites'),('ROADVEH','roadveh_cmd.cpp','_roadveh_images')]:
   body=(REPO/'src'/filename).read_text().split(name+'[] = {',1)[1].split('};',1)[0]
   arrays[feature]=[int(x,0) for x in re.findall(r'0x[0-9a-fA-F]+|\b\d+\b',body)]
  body=(REPO/'src/roadveh_cmd.cpp').read_text().split('_roadveh_full_adder[] = {',1)[1].split('};',1)[0]
  arrays['loaded']=[int(x,0) for x in re.findall(r'\b\d+\b',body)]
 result=[]
 for feature,macro,offset in [('SHIP','SVI',204),('ROADVEH','ROV',116)]:
  for m in re.finditer(macro+r'\((.*?)\), //\s*(\d+) (.+)',text):
   values,identifier,name=m.groups();v=[x.strip() for x in values.split(',')];identifier=int(identifier)
   ship=feature=='SHIP'
   p=dict(info[identifier+offset],source='DEFAULT',feature=feature,id=identifier,name=name,
    speed=int(v[3] if ship else v[4])/2*1.00584,capacity=int(v[4] if ship else v[5]),
    cost_factor=int(v[1]),running_cost_factor=int(v[5] if ship else v[2]),
    loading_speed=10 if ship else 5,refit_cost=8,cargo_age_period=185,retire_early=0,
    sound=v[6] if ship else v[3],image_index=int(v[0]),role='Original default vehicle')
   if ship:p.update(is_refittable=bool(int(v[7])),acceleration=int(v[2]),ocean_fraction=1,canal_fraction=1)
   else:p.update(power=int(v[7])*10,weight=int(v[6])/4,length=8,tractive_effort_coefficient=76/256)
   if graphics:
    climate='base' if 'TEMPERATE' in p['climates'] else 'arctic' if 'ARCTIC' in p['climates'] else 'tropical' if 'TROPICAL' in p['climates'] else 'toyland'
    p['sprites']=[]
    p['loaded_sprites']=[]
    for d in range(8):
     sprite=arrays[feature][p['image_index']]+d
     p['sprites'].append(files[climate].image(mapping[climate][sprite]) if climate in mapping and sprite in mapping[climate] else files['base'].image(sprite))
     if not ship:sprite+=arrays['loaded'][p['image_index']]
     p['loaded_sprites'].append(files[climate].image(mapping[climate][sprite]) if climate in mapping and sprite in mapping[climate] else files['base'].image(sprite))
   result.append(p)
 if len(result)!=99:raise ValueError(f'Expected 99 surface defaults; got {len(result)}')
 return result
