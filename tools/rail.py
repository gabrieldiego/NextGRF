"""Original default-brand rail extension and dated wagon generations.

IDs are permanent and feature-local: locomotives 128-151; wagons use fixed
generation/family/track IDs.
"""

# ID, key, name, year, speed km/h, hp, empty t, cost, running cost, propulsion,
# role, onboard passengers (powered passenger modules can haul normal coaches).
LOCOMOTIVES = [
    (128,'kirby_pioneer','Kirby Paul Pioneer',1804,15,25,10,1,2,'steam','Pioneer light freight',0),
    (129,'wills_colliery','Wills Colliery',1815,20,60,16,2,4,'steam','Colliery freight',0),
    (130,'kirby_courier','Kirby Paul Courier',1825,30,90,18,3,7,'steam','Early passenger and mail',0),
    (131,'chaney_patentee','Chaney Patentee',1835,50,150,24,4,12,'steam','Early express',0),
    (132,'wills_miner','Wills Miner',1850,55,300,38,5,18,'steam','Industrial freight',0),
    (133,'chaney_single','Chaney Single',1865,80,400,45,6,24,'steam','Passenger express',0),
    (134,'ginzu_express','Ginzu Express',1880,100,600,60,8,32,'steam','Long-distance passenger',0),
    (135,'wills_consolidation','Wills Consolidation',1895,70,850,82,10,40,'steam','Heavy freight',0),
    (136,'chaney_atlantic','Chaney Atlantic',1905,110,900,95,11,46,'steam','Passenger express',0),
    (137,'sh_e1','SH E1',1912,90,1200,62,14,40,'electric','Early electric mixed traffic',0),
    (138,'manley_railmotor','Manley-Morel Railmotor',1930,80,180,24,7,24,'diesel','Local passenger railcar',32),
    (139,'mjs_100','MJS 100',1940,48,250,30,6,22,'diesel','Branch freight and shunting',0),
    (140,'sh_e2','SH E2',1950,120,2500,78,20,85,'electric','Electric mixed traffic',0),
    (141,'cs_5000','CS 5000',1988,120,5000,150,28,135,'diesel','Heavy freight',0),
    (142,'floss_67','Floss 67',2000,140,3500,110,24,110,'diesel','Mixed traffic',0),
    (143,'sh_60','SH 60',2010,160,6700,120,35,150,'electric','Heavy freight',0),
    (144,'manley_m300','Manley-Morel M300',2015,160,2200,55,23,85,'electric','Commuter powered passenger module',64),
    (145,'asiastar_2','AsiaStar II',2020,320,9000,95,55,220,'electric','High-speed passenger',0),
    (146,'mjs_1500','MJS 1500',2025,120,2200,85,20,80,'diesel','Economical regional freight',0),
    (147,'manley_m400','Manley-Morel M400',2030,200,3600,62,30,100,'electric','Regional powered passenger module',80),
    (148,'sh_80','SH 80',2035,160,9000,150,46,165,'electric','Heavy freight',0),
    (149,'x3000','X3000',2040,400,11000,100,68,230,'monorail','Monorail express',0),
    (150,'lev5_griffin',"Lev5 'Griffin'",2045,680,18000,115,90,245,'maglev','Maglev express',0),
    (151,'sh_90','SH 90',2050,200,10000,140,52,175,'electric','Fast electric freight',0),
]

# Generation, year, passenger capacity, mail capacity, bulk cargo capacity,
# passenger top speed, freight top speed, reference tare weight, length in eighths.
GENERATIONS = [
    (1,1804,8,10,4,25,20,2,4),
    (2,1835,16,16,8,60,45,4,5),
    (3,1870,28,24,14,100,70,8,6),
    (4,1920,40,32,22,140,100,16,8),
    (5,1960,56,40,32,180,120,20,8),
    (6,1990,64,50,42,230,140,23,8),
    (7,2020,80,65,52,280,160,25,8),
    (8,2040,96,80,64,320,200,27,8),
]

# Fixed family ID, key, display name, capacity kind, default cargo expression,
# cargo classes, explicit allowed refits, disallowed refits, first generation.
FAMILIES = [
    (0,'passenger','Passenger Coach','passengers','PASS',['CC_PASSENGERS'],[],[],1),
    (1,'mail','Mail Van','mail','MAIL',['CC_MAIL'],[],[],1),
    (2,'bulk','Bulk Wagon','bulk','climate == CLIMATE_TROPICAL ? CORE : COAL',['CC_BULK'],[],[],1),
    (3,'box','Covered Van','bulk','GOOD',['CC_PIECE_GOODS','CC_EXPRESS','CC_REFRIGERATED'],[],['PASS','MAIL','LVST','VALU','GOLD','DIAM','WOOD','STEL'],1),
    (4,'tank','Tanker','bulk','OIL_',['CC_LIQUID'],[],[],1),
    (5,'flat','Flat Wagon','bulk','climate == CLIMATE_TROPICAL ? RUBR : WOOD',[],['WOOD','STEL','PAPR','RUBR'],[],1),
    (6,'livestock','Livestock Van','bulk','LVST',[],['LVST'],[],1),
    (7,'refrigerated','Refrigerated Van','bulk','climate == CLIMATE_TEMPERATE ? GOOD : FOOD',[],['GOOD','FOOD','FRUT'],[],3),
    (8,'valuables','Secure Van','bulk','climate == CLIMATE_ARCTIC ? GOLD : climate == CLIMATE_TROPICAL ? DIAM : VALU',['CC_ARMOURED'],[],[],1),
]

TRACKS = {'RAIL': (0,1,1804), 'MONO': (1,6,1998), 'MGLV': (2,7,2020)}
CARGOS = ['COAL','CORE','OIL_','WOOD','STEL','PAPR','RUBR','LVST','FRUT']


def trains():
    result = []
    for row in LOCOMOTIVES:
        fields = ('id','key','name','year','speed','power','weight','cost_factor',
                  'running_cost_factor','propulsion','role','capacity')
        p = dict(zip(fields,row))
        p.update(kind='engine', track={'electric':'ELRL','monorail':'MONO','maglev':'MGLV'}.get(p['propulsion'],'RAIL'),
                 length=6 if p['year']<1830 else 8, vehicle_life=20 if p['year']<1900 else 30,
                 model_life=None if p['year']>=2000 else 40, generation=1 if p['year']<1850 else 3,
                 loading_speed=20 if p['capacity'] else 5, retire_early=0,
                 climates=['TEMPERATE','ARCTIC','TROPICAL'], default_cargo='PASS',
                 cargo_classes=['CC_PASSENGERS'] if p['capacity'] else [],
                 allow=[], disallow=[], tractive_effort_coefficient=.20 if p['year']<1850 else .30,
                 reliability_decay=20, refit_cost=0, cargo_age_period=185)
        result.append(p)
    for track,(track_id,first_generation,first_year) in TRACKS.items():
        for g in GENERATIONS:
            gen,year,pax,mail,bulk,pass_speed,freight_speed,tare,length = g
            if gen<first_generation:
                continue
            for family_id,key,name,capacity_kind,cargo,classes,allow,disallow,first in FAMILIES:
                if gen<first:
                    continue
                passenger = key in ('passenger','mail')
                speed = pass_speed if passenger else freight_speed
                if track == 'MONO': speed = max(speed, 360+(gen-6)*60 if passenger else 180+(gen-6)*30)
                if track == 'MGLV': speed = max(speed, 660+(gen-7)*60 if passenger else 280+(gen-7)*40)
                capacity = {'passengers':pax,'mail':mail,'bulk':bulk}[capacity_kind]
                if key in ('valuables','livestock'): capacity=max(2, bulk*3//4)
                next_year = GENERATIONS[gen][1] if gen<len(GENERATIONS) else None
                p = dict(id=256+track_id*256+(gen-1)*16+family_id,
                         key=f'rail_{track.lower()}_g{gen}_{key}', name=f'G{gen} {name}' + ('' if track=='RAIL' else f' ({track})'),
                         year=max(year,first_year), speed=speed, capacity=capacity,
                         generation=gen, family=key, kind='wagon', propulsion='wagon',track=track,
                         weight=tare+(2 if key in ('passenger','refrigerated','valuables') and gen>=3 else 0),
                         cost_factor=8+gen*12+(6 if passenger else 0)+track_id*12,
                         running_cost_factor=0, length=length,
                         vehicle_life=25 if gen<=3 else 35,
                         model_life=None if next_year is None else max(16,next_year-year+8),
                         retire_early=-5, reliability_decay=20, loading_speed=(2+gen*2 if passenger else 2+gen),
                         refit_cost=0,cargo_age_period=185,tractive_effort_coefficient=.30,
                         default_cargo=cargo,cargo_classes=classes,allow=allow,disallow=disallow,
                         climates=['TEMPERATE','ARCTIC'] if key=='livestock' else ['TEMPERATE','ARCTIC','TROPICAL'],
                         power=0,role=f'Generation {gen} {name.lower()}')
                result.append(p)
    return result
