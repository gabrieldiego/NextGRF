"""NML generator for the additive rail fleet."""
from rail_render import CELL, SHEET_ITEMS


def generate(items):
    lines=['railtypetable { RAIL, ELRL, MONO, MGLV }']
    for row,p in enumerate(items):
        chunk=row//SHEET_ITEMS
        local_row=row%SHEET_ITEMS
        key=p['key']
        for stage in (0,1):
            sprite=f'rail_sprites_{key}_{stage}'
            lines.append(f'spriteset({sprite}, "sprites/rail-{chunk}-1x.png") {{')
            for direction in range(8):
                lines.append(f'[{direction*CELL[0]}, {(local_row*2+stage)*CELL[1]}, {CELL[0]}, {CELL[1]}, {-CELL[0]//2}, {-CELL[1]//2}]')
            lines.append('}')
            for zoom,level in [(2,'ZOOM_LEVEL_IN_2X'),(4,'ZOOM_LEVEL_IN_4X')]:
                lines.append(f'alternative_sprites({sprite}, {level}, BIT_DEPTH_8BPP, "sprites/rail-{chunk}-{zoom}x.png") {{')
                for direction in range(8):
                    lines.append(f'[{direction*CELL[0]*zoom}, {(local_row*2+stage)*CELL[1]*zoom}, {CELL[0]*zoom}, {CELL[1]*zoom}, {-CELL[0]*zoom//2}, {-CELL[1]*zoom//2}]')
                lines.append('}')
        lines.append(f'spritegroup rail_group_{key} {{ loaded: [rail_sprites_{key}_0, rail_sprites_{key}_1]; loading: [rail_sprites_{key}_0, rail_sprites_{key}_1]; }}')
        propulsion=p['propulsion'];wagon=p['kind']=='wagon'
        kind={'wagon':'DIESEL','steam':'STEAM','diesel':'DIESEL','electric':'ELECTRIC','monorail':'MONORAIL','maglev':'MAGLEV'}[propulsion]
        base='NONE' if wagon else 'STEAM' if propulsion=='steam' else 'DIESEL' if propulsion=='diesel' else 'ELECTRIC'
        effect='DISABLE' if wagon or propulsion in ('monorail','maglev') else kind
        # Public NewGRF flag bit 1 enables primary and secondary company colours.
        flags='bitmask(1, TRAIN_FLAG_MU)' if p['capacity'] and not wagon else 'bitmask(1)'
        life='VEHICLE_NEVER_EXPIRES' if p['model_life'] is None else p['model_life']
        classes='bitmask('+', '.join(p['cargo_classes'])+')'
        climates='bitmask('+', '.join('CLIMATE_'+x for x in p['climates'])+')'
        lines.append(f'''item(FEAT_TRAINS, {key}, {p['id']}) {{
 property {{
  name: string(STR_RAIL_{key.upper()});
  climates_available: {climates};
  introduction_date: date({p['year']},1,1);
  model_life: {life}; vehicle_life: {p['vehicle_life']};
  retire_early: {p['retire_early']}; reliability_decay: {p['reliability_decay']};
  loading_speed: {p['loading_speed']}; cargo_age_period: {p['cargo_age_period']};
  cost_factor: {p['cost_factor']}; running_cost_factor: {p['running_cost_factor']};
  running_cost_base: RUNNING_COST_{base};
  sprite_id: SPRITE_ID_NEW_TRAIN;
  track_type: {p['track']}; engine_class: ENGINE_CLASS_{kind};
  speed: {p['speed']} km/h; power: {p['power']} hp; weight: {p['weight']} ton;
  length: {p['length']}; dual_headed: 0;
  cargo_capacity: {p['capacity']}; default_cargo_type: {p['default_cargo']};
  refittable_cargo_classes: {classes}; non_refittable_cargo_classes: 0;
  cargo_allow_refit: [{', '.join(p['allow'])}]; cargo_disallow_refit: [{', '.join(p['disallow'])}];
  refit_cost: 0; misc_flags: {flags};
  tractive_effort_coefficient: {p['tractive_effort_coefficient']};
  air_drag_coefficient: 0.08;
  visual_effect_and_powered: visual_effect_and_powered(VISUAL_EFFECT_{effect}, 0, DISABLE_WAGON_POWER);
  extra_power_per_wagon: 0 hp; extra_weight_per_wagon: 0 ton;
  bitmask_vehicle_info: 0;
  ai_special_flag: {'AI_FLAG_PASSENGER' if p['capacity'] and not wagon else 'AI_FLAG_CARGO'};
 }}
 graphics {{
  default: rail_group_{key}; purchase: rail_sprites_{key}_0;
  additional_text: string(STR_RAIL_ROLE_{key.upper()});
  {'cargo_capacity: return '+str(p['capacity'])+';' if wagon else ''}
 }}
}}
''')
    return '\n'.join(lines)


def strings(items):
    lines=[]
    for p in items:
        key=p['key'].upper()
        lines.append(f"STR_RAIL_{key} :{p['name']}")
        lines.append(f"STR_RAIL_ROLE_{key} :NextGRF | {p['role']}. " +
                     ('Earlier wagons retain their original capacity and speed limit.' if p['kind']=='wagon' else 'Compatible coaches and wagons can be attached.'))
    return '\n'.join(lines)+'\n'
