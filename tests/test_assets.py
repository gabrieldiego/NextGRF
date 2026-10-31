"""Check saved-ID stability, sprite integrity and the additive vehicle contract."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from build import generate_nml
from render import CELL, render
from roster import IDS, aircraft
from ranges import default_ranges
import re


class AircraftTests(unittest.TestCase):
    def test_ids_cannot_replace_default_slots(self):
        planes = aircraft()
        self.assertEqual(len(planes), 20)
        self.assertEqual(len({p['id'] for p in planes}), len(planes))
        self.assertTrue(all(p['id'] >= 41 for p in planes))
        self.assertEqual(IDS['sampson_u12'], 64)
        self.assertEqual(IDS['darwin_800'], 83)
        source = generate_nml(planes)
        self.assertNotIn('disable_item', source)
        self.assertNotIn('engine_override', source)
        self.assertEqual(source.count('item(FEAT_AIRCRAFT'), 61)
        patches = re.findall(r'item\(FEAT_AIRCRAFT, default_range_(\d+), (\d+)\) \{ property \{ (.*?) \} \}', source)
        self.assertEqual(len(patches),41)
        for name,identifier,properties in patches:
            self.assertEqual(name,identifier)
            self.assertRegex(properties,r'^range: \d+;$')
        self.assertEqual({p['id'] for p in default_ranges()},set(range(41)))

    def test_all_sprites_have_margin_transparency_and_company_colours(self):
        for p in aircraft():
            headings = []
            for direction in range(8):
                with self.subTest(aircraft=p['key'], heading=direction):
                    image = render(p, direction)
                    self.assertEqual(image.size, CELL)
                    box = image.getbbox()
                    self.assertIsNotNone(box)
                    self.assertGreater(box[0], 0)
                    self.assertGreater(box[1], 0)
                    self.assertLess(box[2], CELL[0])
                    self.assertLess(box[3], CELL[1])
                    self.assertEqual(image.info['transparency'], 0)
                    self.assertTrue(any(198 <= color <= 205 for count,color in image.getcolors()))
                    headings.append(image.tobytes())
            self.assertEqual(len(set(headings)), 8)

    def test_endgame_has_regional_large_and_supersonic_options(self):
        endgame = [p for p in aircraft() if p['model_life'] is None]
        self.assertTrue(any(p['small'] and p['speed'] < 700 for p in endgame))
        self.assertTrue(any(p['small'] and p['speed'] >= 900 for p in endgame))
        self.assertTrue(any(not p['small'] and p['passengers'] >= 400 for p in endgame))
        self.assertTrue(any(p['speed'] > 2000 for p in endgame))

    def test_mail_plane_and_finite_range_tradeoffs(self):
        planes = {p['key']: p for p in aircraft()}
        self.assertEqual((planes['coleman_courier']['passengers'], planes['coleman_courier']['mail']), (40, 40))
        self.assertTrue(all(0 < p['range'] <= 1600 for p in planes.values()))
        self.assertEqual(planes['bakewell_lb12']['range'],512)
        for p in planes.values():
            if p['passengers']>=220:
                self.assertTrue(1000<=p['range']<=1600,p['name'])
        self.assertLess(planes['yate_zshuttle2']['range'],512)
        self.assertLess(planes['kelling_k2']['range'],512)
        defaults=default_ranges()
        self.assertTrue(all(0<p['range']<=1600 for p in defaults))
        table=(Path(__file__).resolve().parents[3]/'src/table/engines.h').read_text()
        names={int(i):n.strip() for i,n in re.findall(r'AVI\(.*?\), //\s*(\d+) (.+)',table)}
        self.assertEqual({p['id']:p['name'] for p in defaults},names)
        self.assertLess(planes['sampson_u12']['range'], planes['sampson_u26']['range'])
        self.assertLess(planes['coleman_counte']['range'], planes['coleman_count4']['range'])
        self.assertLess(planes['ffp_hyperdart3']['range'], planes['airtaxi_a37']['range'])


if __name__ == '__main__':
    unittest.main()
