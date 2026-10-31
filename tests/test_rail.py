"""Rail ID, generation progression and playable wagon geometry contracts."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from rail import trains, GENERATIONS
from rail_render import render, CELL
from rail_nml import generate


class RailTests(unittest.TestCase):
    def test_permanent_ids_and_no_default_replacements(self):
        items=trains()
        self.assertEqual(len({p['id'] for p in items}),len(items))
        self.assertTrue(all(p['id']>=116 for p in items))
        self.assertEqual(next(p['id'] for p in items if p['key']=='kirby_pioneer'),128)
        self.assertEqual(next(p['id'] for p in items if p['key']=='rail_rail_g1_passenger'),256)
        nml=generate(items)
        self.assertNotIn('disable_item',nml)
        self.assertNotIn('engine_override',nml)

    def test_generations_increase_capacity_and_speed(self):
        wagons=[p for p in trains() if p['kind']=='wagon']
        for track in ['RAIL','MONO','MGLV']:
            for family in {p['family'] for p in wagons}:
                sequence=sorted((p for p in wagons if p['track']==track and p['family']==family),key=lambda p:p['year'])
                for a,b in zip(sequence,sequence[1:]):
                    self.assertGreater(b['capacity'],a['capacity'])
                    self.assertGreater(b['speed'],a['speed'])
                    self.assertGreater(b['year'],a['year'])
        self.assertEqual([g[1] for g in GENERATIONS],[1804,1835,1870,1920,1960,1990,2020,2040])

    def test_early_and_endgame_rolling_stock_exists(self):
        items=trains()
        self.assertTrue(any(p['kind']=='engine' and p['year']==1804 for p in items))
        self.assertTrue(any(p['kind']=='wagon' and p['year']==1804 and p['capacity']>0 for p in items))
        for track in ['RAIL','MONO','MGLV']:
            self.assertTrue(any(p['track']==track and p['kind']=='wagon' and p['model_life'] is None for p in items))

    def test_sprites_are_not_clipped(self):
        for p in trains():
            for direction in range(8):
                image=render(p,direction,loaded=True)
                box=image.getbbox()
                with self.subTest(vehicle=p['key'],direction=direction):
                    self.assertIsNotNone(box)
                    self.assertGreater(box[0],0)
                    self.assertGreater(box[1],0)
                    self.assertLess(box[2],CELL[0])
                    self.assertLess(box[3],CELL[1])


if __name__=='__main__':unittest.main()
