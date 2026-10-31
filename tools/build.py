"""Build NextGRF without touching OpenTTD's source or installed user files."""
import argparse
import hashlib
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

from roster import VERSION, GRFID, aircraft
from render import CELL, write_sheets
from rail import CARGOS, trains
from rail_nml import generate as generate_rail, strings as rail_strings
from rail_render import write_sheets as write_rail_sheets
from surface import surface_vehicles
from surface_nml import generate as generate_surface, strings as surface_strings
from surface_render import write_sheets as write_surface_sheets
from ranges import default_ranges

ROOT = Path(__file__).resolve().parents[1]


def generate_nml(planes):
    lines = [f'''// Generated from tools/roster.py; do not edit this build output.
grf {{
    grfid: "{GRFID}";
    name: string(STR_GRF_NAME);
    desc: string(STR_GRF_DESC);
    version: {VERSION};
    min_compatible_version: 1;
}}
if (!dynamic_engines) {{
    error(ERROR, string(STR_ENGINE_POOL));
}}
cargotable {{ PASS, MAIL, GOOD, VALU, GOLD, DIAM, FOOD, {', '.join(CARGOS)} }}
''']
    for row, p in enumerate(planes):
        key = p["key"]
        lines.append(f'spriteset(sprites_{key}, "sprites/aircraft-1x.png") {{')
        for direction in range(8):
            lines.append(f'    [{direction*CELL[0]}, {row*CELL[1]}, {CELL[0]}, {CELL[1]}, {-CELL[0]//2}, {-CELL[1]//2}]')
        lines.append('}')
        for zoom, level in ((2, "ZOOM_LEVEL_IN_2X"), (4, "ZOOM_LEVEL_IN_4X")):
            lines.append(f'alternative_sprites(sprites_{key}, {level}, BIT_DEPTH_8BPP, "sprites/aircraft-{zoom}x.png") {{')
            for direction in range(8):
                lines.append(f'    [{direction*CELL[0]*zoom}, {row*CELL[1]*zoom}, {CELL[0]*zoom}, {CELL[1]*zoom}, {-CELL[0]*zoom//2}, {-CELL[1]*zoom//2}]')
            lines.append('}')
        life = 'VEHICLE_NEVER_EXPIRES' if p["model_life"] is None else p["model_life"]
        lines.append(f'''item(FEAT_AIRCRAFT, {key}, {p['id']}) {{
    property {{
        name: string(STR_{key.upper()});
        climates_available: bitmask(CLIMATE_TEMPERATE, CLIMATE_ARCTIC, CLIMATE_TROPICAL);
        introduction_date: date({p['year']}, 1, 1);
        model_life: {life};
        vehicle_life: {p['vehicle_life']};
        retire_early: {p['retire_early']};
        reliability_decay: {p['reliability_decay']};
        loading_speed: {p['loading_speed']};
        cargo_age_period: {p['cargo_age_period']};
        cost_factor: {p['cost_factor']};
        running_cost_factor: {p['running_cost_factor']};
        sprite_id: SPRITE_ID_NEW_AIRCRAFT;
        aircraft_type: AIRCRAFT_TYPE_{'SMALL' if p['small'] else 'LARGE'};
        speed: {p['speed']} km/h;
        acceleration: {p['acceleration']};
        passenger_capacity: {p['passengers']};
        mail_capacity: {p['mail']};
        range: {p['range']};
        refit_cost: {p['refit_cost']};
        refittable_cargo_classes: 0;
        non_refittable_cargo_classes: 0;
        cargo_allow_refit: [{', '.join(p['refits'])}];
        cargo_disallow_refit: [];
        misc_flags: 0;
        sound_effect: {p['sound']};
    }}
    graphics {{
        default: sprites_{key};
        purchase: sprites_{key};
        additional_text: string(STR_ROLE_{key.upper()});
    }}
}}
''')
    # Claim the original aircraft slots with a range-only Action 0. Omitting
    # every other property and graphics block preserves the stock definition.
    for p in default_ranges():
        lines.append(f"// DEFAULT: {p['name']}\nitem(FEAT_AIRCRAFT, default_range_{p['id']}, {p['id']}) {{ property {{ range: {p['range']}; }} }}")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nmlc', default='nmlc')
    args = parser.parse_args()
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    planes = aircraft()
    rail = trains()
    surface = surface_vehicles()
    write_sheets(planes, build / 'sprites')
    write_rail_sheets(rail, build / 'sprites')
    write_surface_sheets(surface, build / 'sprites')
    (build / 'nextgrf.nml').write_text(generate_nml(planes)+'\n'+generate_rail(rail)+'\n'+generate_surface(surface))
    (build / 'roster.json').write_text(json.dumps(planes, indent=2) + '\n')
    (build / 'default-aircraft-ranges.json').write_text(json.dumps(default_ranges(), indent=2) + '\n')
    (build / 'rail-roster.json').write_text(json.dumps(rail, indent=2) + '\n')
    (build / 'surface-roster.json').write_text(json.dumps(surface, indent=2) + '\n')
    (build/'lang').mkdir(exist_ok=True)
    (build/'lang/english.lng').write_text((ROOT/'lang/english.lng').read_text()+'\n'+rail_strings(rail)+'\n'+surface_strings(surface))
    command = [args.nmlc, '-l', 'lang', '--grf', 'nextgrf.grf', 'nextgrf.nml']
    subprocess.run(command, cwd=build, check=True)
    digest = hashlib.sha256((build / 'nextgrf.grf').read_bytes()).hexdigest()
    (build / 'SHA256SUMS').write_text(f'{digest}  nextgrf.grf\n')
    package = build / 'nextgrf'
    package.mkdir(exist_ok=True)
    for name in ('README.md', 'LICENSE', 'CREDITS.md'):
        if (ROOT / name).exists():
            shutil.copy2(ROOT / name, package / name)
    shutil.copy2(build / 'nextgrf.grf', package / 'nextgrf.grf')
    with tarfile.open(build / 'nextgrf.tar', 'w', format=tarfile.USTAR_FORMAT) as archive:
        for path in sorted(package.iterdir()):
            info = archive.gettarinfo(str(path), arcname=f'nextgrf/{path.name}')
            info.mtime, info.uid, info.gid, info.uname, info.gname = 0, 0, 0, '', ''
            with path.open('rb') as stream:
                archive.addfile(info, stream)
    with (build/'nextgrf-source.tar.gz').open('wb') as output:
        with gzip.GzipFile(filename='', fileobj=output, mode='wb', mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w', format=tarfile.USTAR_FORMAT) as archive:
                for path in sorted(ROOT.rglob('*')):
                    relative = path.relative_to(ROOT)
                    if not path.is_file() or relative.parts[0] in ('build', '.git', '.nmlcache') or '__pycache__' in relative.parts:
                        continue
                    info = archive.gettarinfo(str(path), arcname=f'nextgrf/{relative}')
                    info.mtime, info.uid, info.gid, info.uname, info.gname = 0, 0, 0, '', ''
                    with path.open('rb') as stream:
                        archive.addfile(info, stream)
    print(f'Built {build / "nextgrf.grf"}: {len(planes)} aircraft + {len(rail)} rail vehicles + {len(surface)} ships/road vehicles; SHA256 {digest}')


if __name__ == '__main__':
    main()
