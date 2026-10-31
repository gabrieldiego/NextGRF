"""Read the 116 untouched default rail vehicle entries for catalogs and QA."""
import configparser
import datetime
from pathlib import Path
import re
from defaults import GRF, REPO
from reference import ensure_reference


def default_trains(graphics=True):
    source=(REPO/'src/table/engines.h').read_text()
    info={}
    for m in re.finditer(r'\b(MT|MM|MW)\(\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),(.*?)//\s*(\d+) (.+)',source):
        kind,days,decay,life,model,tail,identifier,name=m.groups()
        inside=tail.split('LandscapeTypes({',1)[1].split('}',1)[0]
        climates=[name for token,name in [('T','TEMPERATE'),('A','ARCTIC'),('S','TROPICAL'),('Y','TOYLAND')] if token in inside]
        date=datetime.date(1920,1,1)+datetime.timedelta(days=int(days))
        info[int(identifier)]=dict(year=date.year,introduction_date=str(date),climates=climates,
                                  reliability_decay=int(decay),vehicle_life=int(life),model_life=int(model))
    files={};mapping={}
    if graphics:
        gfx=ensure_reference();manifest=configparser.ConfigParser();manifest.read(next(gfx.glob('*.obg')))
        for key in ['base','arctic','tropical','toyland']:files[key]=GRF(gfx/manifest['files'][key])
        landscape=(REPO/'src/table/landscape_sprite.h').read_text()
        for key,token in [('arctic','arctic'),('tropical','tropic'),('toyland','toyland')]:
            body=landscape.split(f'_landscape_spriteindexes_{token}[] = {{',1)[1].split('};',1)[0]
            offset=0;table={}
            for a,b in re.findall(r'\{\s*(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+)\}',body):
                for sprite in range(int(a,16),int(b,16)+1):table[sprite]=offset;offset+=1
            mapping[key]=table
        text=(REPO/'src/table/train_sprites.h').read_text()
        arrays={}
        for name in ['_engine_sprite_base','_engine_sprite_and','_engine_sprite_add','_wagon_full_adder']:
            body=text.split(name+'[] = {',1)[1].split('};',1)[0]
            arrays[name]=[int(x,0) for x in re.findall(r'0x[0-9a-fA-F]+|\b\d+\b',body)]
    result=[]
    for match in re.finditer(r'RVI\((.*?)\), //\s*(\d+) (.+)',source):
        values,identifier,name=match.groups();p=[x.strip() for x in values.split(',')]
        item=dict(info[int(identifier)],id=int(identifier),name=name,source='DEFAULT',
                  kind='wagon' if p[1]=='W' else 'engine',power=int(p[4]),weight=int(p[5]),
                  capacity=int(p[8]),speed=int(p[3])*1.00584,cost_factor=int(p[2]),running_cost_factor=int(p[6]),
                  track={'R':'RAIL','C':'ELRL','O':'MONO','L':'MGLV'}.get(p[9],p[9]),
                  length=8,loading_speed=5,refit_cost=8,cargo_age_period=185,retire_early=0,
                  image_index=int(p[0]),double_headed=p[1]=='M',role='Original default vehicle')
        if graphics:
            climate='base' if 'TEMPERATE' in item['climates'] else 'arctic' if 'ARCTIC' in item['climates'] else 'tropical' if 'TROPICAL' in item['climates'] else 'toyland'
            index=int(p[0]);base=arrays['_engine_sprite_base'][index];add=arrays['_engine_sprite_add'][index];mask=arrays['_engine_sprite_and'][index]
            item['sprites']=[]
            item['loaded_sprites']=[]
            for heading in range(8):
                sprite=base+((heading+add)&mask)
                item['sprites'].append(files[climate].image(mapping[climate][sprite]) if climate in mapping and sprite in mapping[climate] else files['base'].image(sprite))
                sprite+=arrays['_wagon_full_adder'][index]
                item['loaded_sprites'].append(files[climate].image(mapping[climate][sprite]) if climate in mapping and sprite in mapping[climate] else files['base'].image(sprite))
        result.append(item)
    if len(result)!=116:raise ValueError(f'Expected 116 default rail vehicles, got {len(result)}')
    return result
