"""Generate a PDF and sprite atlas of ALL default and NextGRF aircraft."""
import argparse
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont
from defaults import DEFAULT_GFX, REPO, default_aircraft
from pdf import PDF
from render import CELL, canvas, render
from roster import DIRECTIONS, GRFID, RELEASE, VERSION, aircraft
from ranges import default_ranges

ROOT = Path(__file__).resolve().parents[1]
BLUE = (.16,.32,.55)
GREEN = (.07,.40,.32)


def properties(p):
    return [
        ('Origin / vehicle ID', f"{p['source']} / {p['id']}"),
        ('Base introduction date', p.get('introduction_date', f"{p['year']}-01-01")),
        ('Climates', ', '.join(p['climates'])),
        ('Airport class', 'Helicopter / helipad' if p.get('helicopter') else 'Small' if p['small'] else 'Large'),
        ('Passenger / mail capacity', f"{p['passengers']} passengers / {p['mail']} bags"),
        ('Speed', f"{p['speed']:.0f} km/h" + (' (requested; rounded by game)' if p['source'] == 'NEXTGRF' else ' (approximate display)')),
        ('Purchase / running cost factors', f"{p['cost_factor']} / {p['running_cost_factor']}"),
        ('Running cost per passenger', f"{p['running_cost_factor']/p['passengers']:.3f} factor / passenger"),
        ('Vehicle life / model life', f"{p['vehicle_life']} years / " + ('never expires' if p['model_life'] is None else f"{p['model_life']} years")),
        ('Reliability decay / retire early', f"{p['reliability_decay']} / {p['retire_early']} years"),
        ('Acceleration', f"{p['acceleration']} (aircraft acceleration units)"),
        ('Loading speed', f"{p['loading_speed']} units / loading interval"),
        ('Range', f"{p['range']:,} tiles per leg" + (' (stock without NextGRF: unlimited)' if p['source']=='DEFAULT' else '')),
        ('Refit cost / cargo ageing', f"{p['refit_cost']} / every {p['cargo_age_period']} ticks"),
        ('Sound', p['sound']),
    ]


def all_aircraft(gfx):
    planes = default_aircraft(gfx)
    patches={p['id']:p for p in default_ranges()}
    for p in planes:
        p.update(stock_range=p['range'],range_modified_by='NextGRF')
        p.update({k:v for k,v in patches[p['id']].items() if k not in ('id','name')})
    for p in aircraft():
        p['source'] = 'NEXTGRF'
        p['sprites'] = [render(p, direction, 4) for direction in range(8)]
        planes.append(p)
    return sorted(planes, key=lambda p: (p['year'], p['source'], p['name']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--opengfx', type=Path, default=DEFAULT_GFX)
    args = parser.parse_args()
    planes = all_aircraft(args.opengfx)
    by_name = {p['name']: p for p in planes}
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    revision = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=REPO, text=True).strip()
    pdf = PDF()
    pdf.page()
    pdf.rect(0, 0, 595, 240, (.07,.12,.20))
    pdf.text(36, 82, 'NextGRF', 42, True, (1,1,1))
    pdf.text(38, 120, 'THE AIRCRAFT CATALOG', 18, True, (.48,.78,.91))
    pdf.text(38, 154, '1914 - 2050 | Default roster + original extensions', 12, color=(1,1,1))
    pdf.text(38, 185, f'41 DEFAULT aircraft + 20 NEXTGRF aircraft | OpenTTD {revision}', 11, color=(1,1,1))
    pdf.text(36, 278, 'A familiar fleet, extended in both directions', 19, True)
    y = 307
    for paragraph in [
        'Every entry is marked DEFAULT or NEXTGRF. All 41 original aircraft are included, including Toyland aircraft and helicopters. The 20 additions use the same fictional manufacturers. Entries are ordered by base introduction year.',
        'Default values are extracted directly from this OpenTTD checkout. Default sprites are decoded from OpenGFX2 Classic 0.8.1; they are comparison material only and are not included in the playable NextGRF package.',
        'NextGRF sprites are original palette-based mesh renders with eight headings and native 1x, 2x and 4x zoom levels. Blue pixels use the game company-colour palette. NextGRF also patches the range of all 41 default aircraft, including Toyland and helicopters. All other default properties and artwork stay inherited; OpenTTD code is unchanged.',
        'Introduction dates are base dates. OpenTTD can add up to 511 days and an exclusive-preview period before general availability. Speed is quantized by the aircraft format; requested NextGRF speeds can differ from the displayed speed by several km/h.',
        'Ranges are straight-line airport-to-airport distances in map tiles, per flight leg. Each aircraft has an explicit range chosen for its service role. Default entries show the effective range with NextGRF and identify their original unlimited range. These are balance values, not real-world kilometres.',
        'Cost factors are the actual configured multipliers, not fixed prices. Currency, inflation, game settings and other NewGRFs affect the final prices. The per-passenger factor helps compare running-cost efficiency at full occupancy; it is not a profit forecast.',
        'For NextGRF refits, mail gets passengers + mail capacity, goods gets half that sum, and valuables/gold/diamonds or food gets one quarter (rounded to nearest integer). Only cargos present in the selected climate appear. Passengers retain the separate mail compartment.',
        'Future technologies are fictional visual and economic themes. There is no battery, fuel, hydrogen or charging simulation. Large aircraft retain the standard higher crash risk at small airports. Sprite views are enlarged to fit; comparison panels use a common scale. Helicopter images show body sprites; the game adds rotors.',
    ]:
        y = pdf.paragraph(36, y, paragraph, size=10) + 13
    pdf.end_page()
    for offset in range(0, len(planes), 27):
        pdf.page()
        pdf.text(36, 58, 'Fleet index', 25, True)
        pdf.text(36, 82, 'Year | origin | name | passengers + mail | km/h | range (tiles)', 10)
        for index, p in enumerate(planes[offset:offset+27]):
            y = 113 + index * 24
            color = GREEN if p['source'] == 'NEXTGRF' else BLUE
            pdf.text(36, y, str(p['year']), 10, True)
            pdf.text(73, y, p['source'], 8, True, color)
            pdf.text(133, y, p['name'], 10)
            pdf.text(385, y, f"{p['passengers']} + {p['mail']}", 9)
            pdf.text(455, y, f"{p['speed']:.0f}", 9)
            pdf.text(507, y, str(p['range']) if p['range'] else 'Unlimited', 8)
        pdf.end_page()
    pdf.page()
    pdf.text(36, 58, 'Flight range settings', 25, True)
    pdf.paragraph(36, 88, 'Ranges are explicit gameplay settings in map tiles per flight leg. The LB-12 has 512 tiles. Long-haul additions span 1051-1589 tiles; regional aircraft and supersonic express services have shorter missions.', size=10)
    pdf.text(36, 155, 'NEXTGRF AIRCRAFT', 9, True)
    pdf.text(245, 155, 'SERVICE ROLE', 9, True)
    pdf.text(493, 155, 'TILES', 9, True)
    for index, p in enumerate(p for p in planes if p['source'] == 'NEXTGRF'):
        y = 181 + index*25
        if index % 2 == 0:
            pdf.rect(36, y-14, 523, 23, (.95,.96,.97))
        pdf.text(40, y, p['name'], 9)
        pdf.text(245, y, p['range_role'], 8)
        pdf.text(493, y, str(p['range']), 9, True)
    pdf.paragraph(36, 710, 'Short ranges encourage local feeder routes and intermediate airport stops. Regional, long-haul and express aircraft have different service roles. Range applies to every cargo refit and is measured between successive airport orders.', size=9, leading=13)
    pdf.text(36, 785, 'Complete range settings: tools/ranges.py and build/catalog-data.json.', 8)
    pdf.end_page()
    originals=[p for p in planes if p['source']=='DEFAULT']
    for offset in range(0,len(originals),23):
        pdf.page()
        pdf.text(36,58,'Default flight range settings',24,True)
        pdf.paragraph(36,87,'All entries remain DEFAULT vehicles. Stock range is unlimited; NextGRF changes only range, with an explicit tile limit for each service role. Other default properties, sprites and refits are inherited.',size=10)
        pdf.text(36,150,'DEFAULT AIRCRAFT',9,True);pdf.text(245,150,'SERVICE ROLE',9,True);pdf.text(505,150,'TILES',9,True)
        for index,p in enumerate(originals[offset:offset+23]):
            y=177+index*25
            if index%2==0:pdf.rect(36,y-14,523,23,(.95,.96,.97))
            pdf.text(40,y,p['name'],8.5);pdf.text(245,y,p['range_role'],8)
            pdf.text(505,y,p['range'],9,True)
        pdf.text(36,778,'Origin: DEFAULT | Range modified by NextGRF | No new default sprites or vehicle IDs',9)
        pdf.end_page()
    for p in planes:
        pdf.page()
        color = GREEN if p['source'] == 'NEXTGRF' else BLUE
        pdf.rect(36, 31, 81, 22, color)
        pdf.text(44, 46, p['source'], 10, True, (1,1,1))
        pdf.text(130, 46, f"INTRODUCED {p['year']}", 10, True)
        pdf.text(36, 83, p['name'], 22, True)
        for d, sprite in enumerate(p['sprites']):
            col, row = d % 4, d // 4
            x, y = 36 + col*131, 102 + row*105
            pdf.rect(x, y, 128, 101, (.937,.953,.969))
            rgba = sprite.convert('RGBA')
            box = rgba.getchannel('A').getbbox()
            cropped = rgba.crop(box)
            factor = min(110 / cropped.width, 77 / cropped.height)
            w, h = cropped.width * factor, cropped.height * factor
            pdf.image(cropped, x+(128-w)/2, y+4+(77-h)/2, w, h)
            pdf.text(x+58, y+95, DIRECTIONS[d], 8, True)
        y = 336
        for index, (label, value) in enumerate(properties(p)):
            if index % 2 == 0:
                pdf.rect(36, y-13, 523, 22, (.95,.96,.97))
            pdf.text(43, y, label, 9, True)
            pdf.text(245, y, value, 8 if len(value)>45 else 9)
            y += 22
        if p['source'] == 'NEXTGRF':
            pdf.text(36, 677, 'Allowed refits: ' + ', '.join(p['refits']), 9)
            pdf.text(36, 695, 'Graphics: custom, DOS palette, company-colour ramp; flags 0; cargo classes 0.', 9)
            comparator = by_name[p['comparison']]
            pdf.rect(36, 710, 523, 79, (.937,.953,.969))
            pdf.image(comparator['sprites'][6], 40, 711, 93, 77)
            pdf.text(145, 729, f"Compare: {comparator['name']} [{comparator['source']}]", 10, True)
            pdf.text(145, 748, f"{comparator['passengers']} passengers + {comparator['mail']} mail | {comparator['speed']:.0f} km/h", 9)
            pdf.text(145, 767, f"Cost factors: buy {comparator['cost_factor']}, run {comparator['running_cost_factor']}", 9)
        else:
            pdf.paragraph(36, 677, 'Default refits: passenger, mail, armoured and express cargo classes; liquid cargos excluded. Actual cargo labels depend on climate. Default aircraft graphics can be shared between models.', size=9, leading=13)
            pdf.text(36, 730, f"Default image index: {p['image_index']} | source: src/table/engines.h", 9)
            pdf.text(36, 749, 'Default artwork: OpenGFX2 / OpenGFX contributors. Only range is changed by NextGRF.', 9)
            pdf.text(36, 768, f"Range: {p['range']} tiles per flight leg | {p['range_role']}",9)
        pdf.end_page()
    pdf.page()
    pdf.text(36, 58, 'Technical reference and credits', 24, True)
    paragraphs = [
        f'NextGRF version {RELEASE} | GRFID {GRFID} | integer version {VERSION} | minimum compatible version 1. There are no user-configurable parameters in this release. Dynamic engines must be enabled. Vehicle IDs 64-83 are reserved for the 20 additions.',
        'All additions are available in Temperate, Arctic and Tropical climates. Toyland has no additions but its default aircraft also get finite ranges. Historical models expire after their configured manufacturer support period; endgame regional, express and large-aircraft choices never expire. An individual vehicle still ages normally.',
        'All additions use a custom aircraft sprite ID and default aircraft cargo ageing. No cargo capacity callbacks override the standard aircraft refit conversion. Default slots 0-40 receive range-only property changes, without graphics, capacity, cost, refit or other property definitions. Stock properties are verified against no-GRF games.',
        'The build generates 160 directional views at each of three zoom levels (480 sprites). Aircraft geometry and balance are editable in tools/render.py and tools/roster.py. The build/roster.json file contains every configured aircraft property in machine-readable form.',
        'Default data: OpenTTD contributors, src/table/engines.h and src/aircraft_cmd.cpp at the revision on the cover. Default art: OpenGFX2 Classic 0.8.1, OpenGFX2 and OpenGFX contributors, GPL version 2 or later. The pinned release archive checksum is recorded in tools/reference.py.',
        'Original NextGRF code and rendered aircraft art: NextGRF project, GPL version 2. A generated AI artwork study is retained separately in assets/concepts and is not shipped as game sprites. The study was created with the built-in image generation tool; the final game sprites are deterministic original mesh renders.',
        'Reference: https://newgrf-specs.tt-wiki.net/wiki/NML:Vehicles ; https://github.com/OpenTTD/nml ; https://github.com/OpenTTD/OpenGFX2 . The source and license permit inspecting and rebuilding the game package and catalog.',
    ]
    y = 95
    for paragraph in paragraphs:
        y = pdf.paragraph(36, y, paragraph) + 17
    pdf.end_page()
    output = build / 'NextGRF-Catalog.pdf'
    pdf.save(output)
    serializable = [{k:v for k,v in p.items() if k != 'sprites'} for p in planes]
    (build / 'catalog-data.json').write_text(json.dumps(serializable, indent=2) + '\n')
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
    preview = Image.new('RGB', (1100, len(planes)*108+50), '#eff3f7')
    draw = ImageDraw.Draw(preview)
    draw.text((15,12), 'NextGRF / DEFAULT aircraft | Eight headings: N NE E SE S SW W NW', fill='#13273e', font=font)
    for row,p in enumerate(planes):
        y = row*108+50
        draw.text((12,y+7), f"{p['year']}  {p['source']}", fill='#07664f' if p['source']=='NEXTGRF' else '#294c82', font=font)
        draw.text((12,y+28), p['name'], fill='#13273e', font=font)
        for direction, sprite in enumerate(p['sprites']):
            sprite = sprite.resize(CELL, Image.Resampling.NEAREST).convert('RGBA')
            preview.paste(sprite, (320+direction*96,y), sprite)
    preview.save(build / 'fleet-preview.png')
    print(f'Wrote {output}: {len(pdf.pages)} pages, {len(planes)} labeled entries')


if __name__ == '__main__':
    main()
