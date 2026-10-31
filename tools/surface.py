"""Original default-brand ships and road vehicles, with stable feature-local IDs."""
from rail import FAMILIES

# key, name, year, km/h, native cargo capacity, role, purchase, running, hull style
SHIP_ROWS=[
 ('mps_sloop','MPS Coastal Sloop',1700,20,30,'ferry',55,18,'sail'),
 ('ffp_packet','FFP Packet Brig',1725,24,50,'ferry',65,24,'brig'),
 ('yate_coaster','Yate Sailing Coaster',1700,18,60,'cargo',70,22,'sail'),
 ('ffp_clipper','FFP Mail Clipper',1780,32,80,'ferry',85,35,'clipper'),
 ('bakewell_merchant','Bakewell Merchantman',1800,24,120,'cargo',90,32,'brig'),
 ('mps_paddle','MPS Paddle Ferry',1830,28,120,'ferry',100,50,'paddle'),
 ('yate_river','Yate River Steamer',1850,24,150,'cargo',95,42,'paddle'),
 ('ffp_liner','FFP Ocean Liner',1870,36,240,'ferry',135,80,'liner'),
 ('bakewell_barge','Bakewell Oil Barge',1875,22,120,'tanker',90,38,'barge'),
 ('yate_steam','Yate Steam Coaster',1890,28,220,'cargo',115,65,'steamer'),
 ('bakewell_steamer','Bakewell Cargo Steamer',1910,32,350,'cargo',135,85,'steamer'),
 ('mps_motor','MPS Motor Ferry',1925,48,200,'ferry',130,80,'motor'),
 ('yate_coaster2','Yate Coaster II',1945,40,400,'cargo',145,95,'motor'),
 ('bakewell_tanker','Bakewell Ocean Tanker',1955,38,700,'tanker',155,105,'tanker'),
 ('ffp_300','FFP 300 Ferry',1960,50,300,'ferry',155,110,'liner'),
 ('bakewell_boxship','Bakewell Boxship',1975,42,680,'cargo',165,120,'container'),
 ('yate_container','Yate Container Carrier',1990,48,980,'cargo',185,150,'container'),
 ('bakewell_supertanker','Bakewell Supertanker',2000,44,1600,'tanker',205,180,'tanker'),
 ('mps_catamaran','MPS Catamaran',2005,72,180,'ferry',165,125,'catamaran'),
 ('bakewell_feeder','Bakewell Feeder',2020,55,1200,'cargo',205,170,'container'),
 ('ffp_eferry','FFP Electric Ferry',2035,65,400,'ferry',195,115,'electric'),
 ('yate_ocean','Yate Ocean Carrier',2040,60,1800,'cargo',225,200,'container'),
 ('bakewell_ecotanker','Bakewell Eco Tanker',2045,52,2600,'tanker',240,215,'tanker'),
 ('bakewell_oceanmax','Bakewell OceanMax',2050,64,2400,'cargo',245,230,'container'),
 ('mps_hydrofoil','MPS Hydrofoil',2050,100,240,'ferry',220,160,'hydrofoil'),
]

# key, name, year, km/h, passengers, hp, empty t, purchase factor, running factor
BUSES=[
 ('mps_steam_bus','MPS Steam Omnibus',1886,16,12,20,5,30,35),
 ('mps_motor_bus','MPS Motor Omnibus',1895,24,14,30,4,40,40),
 ('foster_townbus','Foster Townbus',1905,32,22,50,5,50,45),
 ('mps_regal1','MPS Regal I',1920,44,28,70,6,65,55),
 ('foster_citybus','Foster Citybus',1935,60,36,100,7,85,70),
 ('mps_regal2','MPS Regal II',1950,76,45,150,9,105,85),
 ('foster_regional','Foster Regional',1965,92,55,220,11,125,100),
 ('mps_metrobus','MPS Metrobus',1980,100,75,280,12,145,115),
 ('foster_high_capacity','Foster High-Capacity Bus',1995,100,110,340,17,180,145),
 ('mps_hybrid_bus','MPS Hybrid Citybus',2010,105,90,320,14,190,130),
 ('foster_ebus','Foster E-Bus',2025,110,100,360,15,200,120),
 ('mps_express_bus','MPS Express Coach',2035,140,70,450,14,215,145),
 ('foster_doubledeck','Foster Doubledeck',2040,120,150,500,20,230,155),
 ('mps_electric_coach','MPS Electric Coach',2050,160,100,550,17,245,160),
]

# Cargo bodies progress independently of the passenger buses.
ROAD_GENERATIONS=[(1,1896,24,3,3,30),(2,1915,36,6,4,60),(3,1935,52,10,5,100),
                  (4,1955,72,16,7,160),(5,1975,90,22,9,250),(6,1995,110,30,11,360),
                  (7,2020,120,40,14,480),(8,2040,140,50,16,600)]
ROAD_FAMILIES=[('box','Balogh',0),('bulk','Uhl',1),('tank','Witcombe',2),('flat','Hereford',3),
               ('livestock','Talbott',4),('refrigerated','Foster',5),('valuables','Perry',6)]


def surface_vehicles():
 result=[]
 for index,row in enumerate(SHIP_ROWS):
  key,name,year,speed,capacity,family,cost,running,shape=row
  ferry=family=='ferry';tank=family=='tanker'
  classes=['CC_PASSENGERS','CC_MAIL'] if ferry else ['CC_LIQUID'] if tank else ['CC_BULK','CC_PIECE_GOODS','CC_EXPRESS','CC_REFRIGERATED','CC_OVERSIZED','CC_ARMOURED']
  result.append(dict(id=32+index,key=key,name=name,year=year,speed=speed,capacity=capacity,
   feature='SHIP',family=family,shape=shape,cost_factor=cost,running_cost_factor=running,
   default_cargo='PASS' if ferry else 'OIL_' if tank else 'GOOD',cargo_classes=classes,allow=[],disallow=[] if tank else ['PASS','MAIL'] if not ferry else [],
   climates=['TEMPERATE','ARCTIC','TROPICAL'],vehicle_life=30 if year<1900 else 35,model_life=None if year>=2000 else 45,
   loading_speed=8 if year<1850 else 15 if year<1950 else 25 if ferry else 40,
   reliability_decay=20,retire_early=0,refit_cost=0,cargo_age_period=185,
   hull_length=44 if year<1800 else 54 if year<1900 else min(110,60+capacity//40),
   canal_fraction=1 if year<1900 else .75 if ferry else .60, ocean_fraction=1,
   power=0,weight=0,length=8,role=('Passenger and mail refits' if ferry else 'Liquid cargoes' if tank else 'Dry cargoes'),generation=0))
 for index,row in enumerate(BUSES):
  key,name,year,speed,capacity,power,weight,cost,running=row
  result.append(dict(id=128+index,key=key,name=name,year=year,speed=speed,capacity=capacity,
   feature='ROADVEH',family='bus',shape='doubledeck' if 'doubledeck' in key else 'coach' if 'coach' in key else 'bus',cost_factor=cost,running_cost_factor=running,
   default_cargo='PASS',cargo_classes=['CC_PASSENGERS'],allow=[],disallow=[],climates=['TEMPERATE','ARCTIC','TROPICAL'],
   vehicle_life=12 if year<1950 else 18,model_life=None if year>=2025 else 30,
   loading_speed=3 if year<1930 else 8 if year<1980 else 16,reliability_decay=20,retire_early=0,refit_cost=0,cargo_age_period=185,
   power=power,weight=weight,length=6 if year<1930 else 8,role='Passenger road service',generation=0))
 lookup={row[1]:row for row in FAMILIES}
 for gen,year,speed,capacity,weight,power in ROAD_GENERATIONS:
  for family,brand,identifier in ROAD_FAMILIES:
   if family=='refrigerated' and gen==1:continue
   _,_,name,_,cargo,classes,allow,disallow,_=lookup[family]
   if family=='box':
    classes=classes+['CC_MAIL'];disallow=[c for c in disallow if c!='MAIL']
   result.append(dict(id=256+(gen-1)*16+identifier,key=f'road_g{gen}_{family}',name=f'{brand} G{gen} {name}',year=year,speed=speed,capacity=capacity,
    feature='ROADVEH',family=family,shape=family,cost_factor=40+gen*20,running_cost_factor=30+gen*18,
    default_cargo=cargo,cargo_classes=classes,allow=allow,disallow=disallow,
    climates=['TEMPERATE','ARCTIC'] if family=='livestock' else ['TEMPERATE','ARCTIC','TROPICAL'],
    vehicle_life=12 if year<1950 else 18,model_life=None if gen==8 else 30,
    loading_speed=2+gen,reliability_decay=20,retire_early=-3,refit_cost=0,cargo_age_period=185,
    power=power,weight=weight,length=6 if gen<=2 else 8,role=f'Generation {gen} cargo road vehicle',generation=gen))
 # Keep a purchase option available continuously in each shipping role.
 # Historical models overlap their successor by twelve years.
 for p in result:
  if p['feature']!='SHIP' or p['model_life'] is None:continue
  successors=[q['year'] for q in result if q['feature']=='SHIP' and q['family']==p['family'] and q['year']>p['year']]
  p['model_life']=max(30,min(successors)-p['year']+12) if successors else None
 return result
