"""Exercise surface purchase lists, construction and every offered cargo refit."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
from reference import ROOT, ensure_reference
from smoke_test import INFO, squirrel
from surface import surface_vehicles
from surface_defaults import default_surface

SCRIPT='''class NextGRFSurfaceQA extends AIController {
 function Check(ok,message) { if(!ok) throw "SURFACE_QA_FAIL: "+message; }
 function Start() {
  AIController.SetCommandDelay(1);AICompany.SetLoanAmount(AICompany.GetMaxLoanAmount());
  local depots={};local built=0;local refitted=0;
  foreach(test in TESTS) {
   local vt=test.ship ? AIVehicle.VT_WATER : AIVehicle.VT_ROAD;
   local all=AIEngineList(vt);Check(all.Count()==test.total,"surface total "+all.Count());
   local actual={};foreach(e,u in all) {local name=AIEngine.GetName(e);if(name!=null) actual[name] <- e;}
   foreach(p in test.items) {
    Check(p.name in actual,"missing "+p.name);local e=actual[p.name];
    Check(AIEngine.GetCapacity(e)==p.capacity,"capacity "+p.name);
    Check(abs(AIEngine.GetMaxSpeed(e)*1.00584-p.speed)<3,"speed "+p.name);
    Check(AIEngine.GetPrice(e)>0,"price "+p.name);
    if(!test.ship) {
     Check(AIEngine.GetPower(e)==p.power,"power "+p.name);
     Check(AIEngine.GetWeight(e)==p.weight,"weight "+p.name);
    }
    if(p.family=="box" || p.family=="ferry") foreach(c,u in AICargoList()) if(AICargo.GetCargoLabel(c)=="MAIL") Check(AIEngine.CanRefitCargo(e,c),"mail refit available "+p.name);
    if(!BUILD) continue;
    if(!(vt in depots)) {
     local depot=-1;
     if(test.ship) {
      for(local y=4;y<120 && depot<0;y++) for(local x=4;x<120 && depot<0;x++) {
       local t=AIMap.GetTileIndex(x,y);local front=AIMap.GetTileIndex(x+1,y);
       if(AITile.IsWaterTile(t) && AITile.IsWaterTile(front) && AIMarine.BuildWaterDepot(t,front)) depot=t;
      }
     } else {
      AIRoad.SetCurrentRoadType(AIRoad.ROADTYPE_ROAD);
      for(local y=8;y<110 && depot<0;y+=4) for(local x=8;x<110 && depot<0;x+=4) {
       local t=AIMap.GetTileIndex(x,y);if(AIRoad.BuildRoadDepot(t,AIMap.GetTileIndex(x+1,y))) depot=t;
      }
     }
     Check(depot>=0,"build depot "+p.name);depots[vt] <- depot;
    }
    local v=AIVehicle.BuildVehicle(depots[vt],e);
    Check(AIVehicle.IsValidVehicle(v),"build "+p.name);built++;
    foreach(c,u in AICargoList()) if(AIEngine.CanRefitCargo(e,c)) {
     Check(AIVehicle.RefitVehicle(v,c),"refit "+p.name);
     Check(AIVehicle.GetCapacity(v,c)==p.capacity,"refitted capacity "+p.name+":"+AICargo.GetCargoLabel(c));refitted++;
    }
    Check(AIVehicle.SellVehicle(v),"sell "+p.name);
   }
  }
  print("SURFACE_QA_PASS built="+built+" refits="+refitted);while(true) this.Sleep(1000);
 }
}
'''


def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--openttd',type=Path,default=ROOT.parents[1]/'build/openttd');args=parser.parse_args()
 game=ROOT/'build/surface-qa'
 for path in ['ai/NextGRFSurfaceQA','newgrf','scripts','baseset','home']:(game/path).mkdir(parents=True,exist_ok=True)
 shutil.copy2(ROOT/'build/nextgrf.tar',game/'newgrf/nextgrf.tar')
 (game/'ai/NextGRFSurfaceQA/info.nut').write_text(INFO.replace('NextGRFQA','NextGRFSurfaceQA').replace('NextGRF QA','NextGRF Surface QA').replace('NXQA','NXSQ'))
 (game/'scripts/game_start.scr').write_text('start_ai "NextGRF Surface QA"\n')
 for path in (ROOT.parents[1]/'build/baseset',Path('/usr/share/games/openttd/baseset')):
  if path.exists():
   for child in path.iterdir():
    dest=game/'baseset'/child.name
    if not dest.exists():dest.symlink_to(child.resolve(),target_is_directory=child.is_dir())
 ref=game/'baseset/opengfx2'
 if not ref.exists():ref.symlink_to(ensure_reference(),target_is_directory=True)
 new=surface_vehicles();defaults=default_surface(False);results=[]
 cases=[(1705,'temperate',True),(1805,'temperate',False),(1890,'temperate',True),(1930,'temperate',False),(1970,'temperate',False),(2000,'temperate',False),(2055,'temperate',True),(2055,'arctic',True),(2055,'tropic',True),(2055,'toyland',False)]
 for year,climate,build in cases:
  cn={'temperate':'TEMPERATE','arctic':'ARCTIC','tropic':'TROPICAL','toyland':'TOYLAND'}[climate];tests=[]
  for feature in ['SHIP','ROADVEH']:
   available=[p for p in new if p['feature']==feature and p['year']<=year and cn in p['climates']]
   base=[p for p in defaults if p['feature']==feature and p['year']<=year and cn in p['climates']]
   tests.append(dict(ship=feature=='SHIP',total=len(base)+len(available),items=[{k:p[k] for k in ['name','capacity','speed','power','weight','family']} for p in available]))
  (game/'ai/NextGRFSurfaceQA/main.nut').write_text(SCRIPT.replace('TESTS',squirrel(tests)).replace('BUILD','true' if build else 'false'))
  cfg=game/'test.cfg';cfg.write_text(f'''[misc]
language = english.lng
[gui]
autosave = off
pause_on_newgame = false
[game_creation]
starting_year = {year}
landscape = {climate}
map_x = 7
map_y = 7
generation_seed = 42
[difficulty]
number_towns = 0
industry_density = 0
terrain_type = 0
quantity_sea_lakes = 2
max_no_competitors = 0
max_loan = 2000000
[vehicle]
dynamic_engines = true
never_expire_vehicles = true
[newgrf]
nextgrf.tar/nextgrf/nextgrf.grf =
''')
  env=dict(os.environ,HOME=str(game/'home'),XDG_DATA_HOME=str(game/'home'),XDG_CONFIG_HOME=str(game/'home'))
  r=subprocess.run([str(args.openttd.resolve()),'-X','-x','-I','OpenGFX2 Classic','-c',str(cfg),'-g','-vnull:ticks=15000','-snull','-mnull','-dscript=2,grf=0'],cwd=game,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=90)
  log=game/f'{year}-{climate}.log';log.write_text(r.stdout)
  if r.returncode or 'SURFACE_QA_PASS' not in r.stdout or 'SURFACE_QA_FAIL' in r.stdout:
   print(r.stdout[-6000:]);raise SystemExit(f'Surface QA failed: {log}')
  record=dict(year=year,climate=climate,new=sum(len(t['items']) for t in tests),build_refit=build,result='PASS');results.append(record);print(record,flush=True)
 (ROOT/'build/surface-qa-results.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':main()
