"""Run real OpenTTD rail-generation, build, refit and coupling checks."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
from rail import trains
from rail_defaults import default_trains
from reference import ensure_reference, ROOT
from smoke_test import INFO, squirrel

SCRIPT='''class NextGRFRailQA extends AIController {
 function Check(ok,message) { if (!ok) throw "RAIL_QA_FAIL: " + message; }
 function Start() {
  AIController.SetCommandDelay(1);
  local actual={}; local all=AIEngineList(AIVehicle.VT_RAIL);
  Check(all.Count()==TOTAL,"total rail count: " + all.Count());
  foreach(e,u in all) { local name=AIEngine.GetName(e); if(name!=null) actual[name] <- e; }
  local expected=EXPECTED;
  AICompany.SetLoanAmount(AICompany.GetMaxLoanAmount());
  local depots={};local carriers={};local built=0;local refitted=0;
  foreach(p in expected) {
   Check(p.name in actual,"missing "+p.name);
   local e=actual[p.name];
   Check(AIEngine.IsWagon(e)==p.wagon,"wagon classification "+p.name);
   Check(AIEngine.GetCapacity(e)==(p.capacity==0 ? -1 : p.capacity),"engine capacity "+p.name);
   Check(abs(AIEngine.GetMaxSpeed(e)*1.00584-p.speed)<3,"speed "+p.name);
   if(!p.wagon) Check(AIEngine.GetPower(e)==p.power,"power "+p.name);
   Check(AIEngine.GetWeight(e)==p.weight,"weight "+p.name);
   Check(AIEngine.GetPrice(e)>0,"price "+p.name);
   if (!BUILD) continue;
   local rt=AIEngine.GetRailType(e);
   if (!(rt in depots)) {
    AIRail.SetCurrentRailType(rt);local depot=-1;
    for(local y=8;y<110 && depot<0;y+=4) for(local x=8;x<110 && depot<0;x+=4) {
     local t=AIMap.GetTileIndex(x,y);
     if(AIRail.BuildRailDepot(t,AIMap.GetTileIndex(x+1,y))) depot=t;
    }
    Check(depot>=0,"build depot "+p.name);depots[rt] <- depot;
   }
   if(!p.wagon) {
    local v=AIVehicle.BuildVehicle(depots[rt],e);
    Check(AIVehicle.IsValidVehicle(v),"build engine "+p.name);built++;
    Check(AIVehicle.SellVehicle(v),"sell engine "+p.name);
   } else {
    if(!(rt in carriers)) {
     local carrier=-1;
     foreach(candidate,u in all) if(!AIEngine.IsWagon(candidate) && AIEngine.GetRailType(candidate)==rt) {
      carrier=AIVehicle.BuildVehicle(depots[rt],candidate);
      if(AIVehicle.IsValidVehicle(carrier)) break;
     }
     Check(AIVehicle.IsValidVehicle(carrier),"wagon carrier "+p.name);carriers[rt] <- carrier;
    }
    local v=AIVehicle.BuildVehicle(depots[rt],e);
    Check(AIVehicle.IsValidVehicle(v),"build wagon "+p.name);built++;
    Check(AIVehicle.MoveWagon(v,0,carriers[rt],0),"couple wagon "+p.name);
    foreach(c,u in AICargoList()) if(AIEngine.CanRefitCargo(e,c)) {
     Check(AIVehicle.RefitVehicle(carriers[rt],c),"refit wagon "+p.name);
     local base=0;
     if(AIEngine.CanRefitCargo(AIVehicle.GetEngineType(carriers[rt]),c)) base=AIEngine.GetCapacity(AIVehicle.GetEngineType(carriers[rt]));
     Check(AIVehicle.GetCapacity(carriers[rt],c)==p.capacity+base,"refitted capacity "+p.name+":"+AICargo.GetCargoLabel(c));refitted++;
    }
    Check(AIVehicle.GetWagonEngineType(carriers[rt],1)==e,"generation ID stable after coupling/refit "+p.name);
    Check(AIVehicle.SellWagon(carriers[rt],1),"sell wagon "+p.name);
   }
  }
  foreach(rt,v in carriers) Check(AIVehicle.SellVehicle(v),"sell carrier");
  print("RAIL_QA_PASS built="+built+" refits="+refitted);
  while(true) this.Sleep(1000);
 }
}
'''


def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--openttd',type=Path,default=ROOT.parents[1]/'build/openttd');args=parser.parse_args()
 game=ROOT/'build/rail-qa'
 for path in ['ai/NextGRFRailQA','newgrf','scripts','baseset','home']:(game/path).mkdir(parents=True,exist_ok=True)
 shutil.copy2(ROOT/'build/nextgrf.tar',game/'newgrf/nextgrf.tar')
 (game/'ai/NextGRFRailQA/info.nut').write_text(INFO.replace('NextGRFQA','NextGRFRailQA').replace('NextGRF QA','NextGRF Rail QA').replace('NXQA','NXRQ'))
 (game/'scripts/game_start.scr').write_text('start_ai "NextGRF Rail QA"\n')
 for path in (ROOT.parents[1]/'build/baseset',Path('/usr/share/games/openttd/baseset')):
  if path.exists():
   for child in path.iterdir():
    destination=game/'baseset'/child.name
    if not destination.exists():destination.symlink_to(child.resolve(),target_is_directory=child.is_dir())
 reference=game/'baseset/opengfx2'
 if not reference.exists():reference.symlink_to(ensure_reference(),target_is_directory=True)
 defaults=default_trains(False);new=trains();results=[]
 cases=[(1820,'temperate',True),(1845,'temperate',False),(1880,'temperate',False),(1930,'temperate',False),(1970,'temperate',False),(2000,'temperate',False),(2030,'temperate',False),(2055,'temperate',True),(2055,'arctic',True),(2055,'tropic',True),(2055,'toyland',False)]
 for year,climate,build in cases:
  climate_name={'temperate':'TEMPERATE','arctic':'ARCTIC','tropic':'TROPICAL','toyland':'TOYLAND'}[climate]
  available=[p for p in new if p['year']<=year and climate_name in p['climates']]
  baseline=[p for p in defaults if p['year']<=year and climate_name in p['climates']]
  expected=[dict(name=p['name'],wagon=p['kind']=='wagon',capacity=p['capacity'],speed=p['speed'],power=p['power'],weight=p['weight']) for p in available]
  (game/'ai/NextGRFRailQA/main.nut').write_text(SCRIPT.replace('EXPECTED',squirrel(expected)).replace('TOTAL',str(len(available)+len(baseline))).replace('BUILD','true' if build else 'false'))
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
quantity_sea_lakes = 0
max_no_competitors = 0
max_loan = 2000000
[vehicle]
dynamic_engines = true
never_expire_vehicles = true
wagon_speed_limits = true
[newgrf]
nextgrf.tar/nextgrf/nextgrf.grf =
''')
  env=dict(os.environ,HOME=str(game/'home'),XDG_DATA_HOME=str(game/'home'),XDG_CONFIG_HOME=str(game/'home'))
  result=subprocess.run([str(args.openttd.resolve()),'-X','-x','-I','OpenGFX2 Classic','-c',str(cfg),'-g','-vnull:ticks=15000','-snull','-mnull','-dscript=2,grf=0'],cwd=game,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=90)
  log=game/f'{year}-{climate}.log';log.write_text(result.stdout)
  if result.returncode or 'RAIL_QA_PASS' not in result.stdout or 'RAIL_QA_FAIL' in result.stdout:
   print(result.stdout[-6000:]);raise SystemExit(f'Rail QA failed: {log}')
  record=dict(year=year,climate=climate,new=len(available),defaults=len(baseline),build_refit_couple=build,result='PASS');results.append(record);print(record,flush=True)
 (ROOT/'build/rail-qa-results.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':main()
