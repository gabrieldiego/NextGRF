"""NML for original additive ships and road vehicles."""
from surface_render import CELLS, SHEET_ITEMS


def generate(items):
 lines=['roadtypetable { ROAD }'];counts={f:0 for f in CELLS}
 for p in items:
  feature=p['feature'];cell=CELLS[feature];row=counts[feature];counts[feature]+=1
  chunk=row//SHEET_ITEMS;local=row%SHEET_ITEMS;key=p['key']
  for stage in (0,1):
   sprite=f'surface_sprites_{key}_{stage}'
   lines.append(f'spriteset({sprite}, "sprites/{feature.lower()}-{chunk}-1x.png") {{')
   for d in range(8):lines.append(f'[{d*cell[0]}, {(local*2+stage)*cell[1]}, {cell[0]}, {cell[1]}, {-cell[0]//2}, {-cell[1]//2}]')
   lines.append('}')
   for zoom,level in [(2,'ZOOM_LEVEL_IN_2X'),(4,'ZOOM_LEVEL_IN_4X')]:
    lines.append(f'alternative_sprites({sprite}, {level}, BIT_DEPTH_8BPP, "sprites/{feature.lower()}-{chunk}-{zoom}x.png") {{')
    for d in range(8):lines.append(f'[{d*cell[0]*zoom}, {(local*2+stage)*cell[1]*zoom}, {cell[0]*zoom}, {cell[1]*zoom}, {-cell[0]*zoom//2}, {-cell[1]*zoom//2}]')
    lines.append('}')
  lines.append(f'spritegroup surface_group_{key} {{ loaded: [surface_sprites_{key}_0, surface_sprites_{key}_1]; loading: [surface_sprites_{key}_0, surface_sprites_{key}_1]; }}')
  life='VEHICLE_NEVER_EXPIRES' if p['model_life'] is None else p['model_life']
  specific=(f'''is_refittable: 1;
  ocean_speed_fraction: {p['ocean_fraction']}; canal_speed_fraction: {p['canal_fraction']};
  sound_effect: SOUND_DEPARTURE_CARGO_SHIP;''' if feature=='SHIP' else f'''road_type: ROAD;
  running_cost_base: RUNNING_COST_ROADVEH;
  power: {p['power']} hp; weight: {p['weight']} ton; length: {p['length']};
  tractive_effort_coefficient: 0.30; air_drag_coefficient: 0.08;
  sound_effect: SOUND_DEPARTURE_{'OLD_BUS' if p['year']<1950 else 'MODERN_BUS'};''')
  lines.append(f'''item(FEAT_{'SHIPS' if feature=='SHIP' else 'ROADVEHS'}, {key}, {p['id']}) {{
 property {{
  name: string(STR_SURFACE_{key.upper()});
  climates_available: bitmask({', '.join('CLIMATE_'+c for c in p['climates'])});
  introduction_date: date({p['year']},1,1);
  model_life: {life}; vehicle_life: {p['vehicle_life']};
  retire_early: {p['retire_early']}; reliability_decay: {p['reliability_decay']};
  loading_speed: {p['loading_speed']}; cargo_age_period: {p['cargo_age_period']};
  cost_factor: {p['cost_factor']}; running_cost_factor: {p['running_cost_factor']};
  sprite_id: SPRITE_ID_NEW_{feature}; speed: {p['speed']} km/h;
  cargo_capacity: {p['capacity']}; default_cargo_type: {p['default_cargo']};
  refittable_cargo_classes: bitmask({', '.join(p['cargo_classes'])}); non_refittable_cargo_classes: 0;
  cargo_allow_refit: [{', '.join(p['allow'])}]; cargo_disallow_refit: [{', '.join(p['disallow'])}];
  refit_cost: 0; misc_flags: bitmask(1);
  {specific}
 }}
 graphics {{
  default: surface_group_{key}; purchase: surface_sprites_{key}_0;
  cargo_capacity: return {p['capacity']};
  additional_text: string(STR_SURFACE_ROLE_{key.upper()});
 }}
}}
''')
 return '\n'.join(lines)


def strings(items):
 return '\n'.join(f"STR_SURFACE_{p['key'].upper()} :{p['name']}\nSTR_SURFACE_ROLE_{p['key'].upper()} :NextGRF | {p['role']}. Capacity is in native cargo units per vehicle." for p in items)+'\n'
