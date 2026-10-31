"""Surface roster progression, native capacities and sprite bounds."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from surface import surface_vehicles, ROAD_GENERATIONS
from surface_render import render, CELLS


class SurfaceTests(unittest.TestCase):
 def test_additive_ids_and_introduction_coverage(self):
  items=surface_vehicles()
  for feature,baseline,first in [('SHIP',11,1700),('ROADVEH',88,1886)]:
   subset=[p for p in items if p['feature']==feature]
   self.assertEqual(len({p['id'] for p in subset}),len(subset))
   self.assertTrue(all(p['id']>=baseline for p in subset))
   self.assertEqual(min(p['year'] for p in subset),first)
   self.assertEqual(max(p['year'] for p in subset),2050)
  for family in {p['family'] for p in items if p['feature']=='ROADVEH' and p['generation']}:
   sequence=sorted((p for p in items if p['feature']=='ROADVEH' and p['family']==family),key=lambda p:p['year'])
   for a,b in zip(sequence,sequence[1:]):
    self.assertGreater(b['capacity'],a['capacity']);self.assertGreater(b['speed'],a['speed'])

 def test_surface_sprite_bounds(self):
  for p in surface_vehicles():
   for d in range(8):
    image=render(p,d,loaded=True);box=image.getbbox();cell=CELLS[p['feature']]
    with self.subTest(vehicle=p['key'],direction=d):
     self.assertIsNotNone(box);self.assertGreater(box[0],0);self.assertGreater(box[1],0)
     self.assertLess(box[2],cell[0]);self.assertLess(box[3],cell[1])

 def test_ship_purchase_windows_cover_each_role(self):
  ships=[p for p in surface_vehicles() if p['feature']=='SHIP']
  for family,first in [('ferry',1700),('cargo',1700),('tanker',1875)]:
   for year in range(first,2101):
    self.assertTrue(any(p['family']==family and p['year']<=year and (p['model_life'] is None or year<=p['year']+p['model_life']) for p in ships),f'{family}: {year}')


if __name__=='__main__':unittest.main()
