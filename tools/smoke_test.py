"""Exercise the compiled GRF using OpenTTD's real NoAI API in isolated games.

No network server, GUI, user saves, profile configuration or source modifications.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

from defaults import default_aircraft
from roster import aircraft
from reference import ensure_reference
from ranges import default_ranges

ROOT = Path(__file__).resolve().parents[1]

INFO = '''class NextGRFQAInfo extends AIInfo {
    function GetAuthor() { return "NextGRF project"; }
    function GetName() { return "NextGRF QA"; }
    function GetShortName() { return "NXQA"; }
    function GetDescription() { return "Isolated NextGRF integration checks"; }
    function GetVersion() { return 1; }
    function GetDate() { return "2026-10-30"; }
    function GetAPIVersion() { return "16"; }
    function CreateInstance() { return "NextGRFQA"; }
    function UseAsRandomAI() { return false; }
}
RegisterAI(NextGRFQAInfo());
'''

SCRIPT = '''class NextGRFQA extends AIController {
    function Check(condition, message) {
        if (!condition) throw "NEXTGRF_QA_FAIL: " + message;
    }
    function Start() {
        AIController.SetCommandDelay(1);
        local actual = {};
        foreach (engine, unused in AIEngineList(AIVehicle.VT_AIR)) {
            local name = AIEngine.GetName(engine);
            actual[name] <- engine;
            local refits="";
            foreach(c,u in AICargoList()) if(AIEngine.CanRefitCargo(engine,c)) refits+=AICargo.GetCargoLabel(c)+",";
            print("NEXTGRF_ENGINE|" + name + "|" + AIEngine.GetCapacity(engine) + "|" + AIEngine.GetMaxSpeed(engine) + "|" + AIEngine.GetPrice(engine) + "|" + AIEngine.GetRunningCost(engine) + "|" + AIEngine.GetPlaneType(engine) + "|" + refits);
        }
        local expected = EXPECTED;
        Check(actual.len() == expected.len(), "aircraft count " + actual.len() + " expected " + expected.len());
        foreach (p in expected) {
            Check(p.name in actual, "missing " + p.name);
            local e = actual[p.name];
            Check(AIEngine.GetCapacity(e) == p.capacity, "capacity " + p.name);
            Check(AIEngine.GetPlaneType(e) == p.type, "airport class " + p.name);
            Check(abs(AIEngine.GetMaxSpeed(e)*4*1.00584 - p.speed) < 18, "speed " + p.name);
            Check(AIEngine.GetPrice(e) > 0 && AIEngine.GetRunningCost(e) > 0, "cost " + p.name);
            Check(AIEngine.GetMaximumOrderDistance(e) == p.range*p.range, "engine range " + p.name);
            if (p.added) {
                foreach (cargo, unused in AICargoList()) {
                    local label = AICargo.GetCargoLabel(cargo);
                    local wanted = false;
                    foreach (allowed in p.refits) if (allowed == label) wanted = true;
                    Check(AIEngine.CanRefitCargo(e, cargo) == wanted, "refit " + p.name + ":" + label);
                }
            }
        }
        BUILD_CHECKS
        print("NEXTGRF_QA_PASS");
        while (true) this.Sleep(1000);
    }
}
'''

BUILD_CHECKS = '''
        AICompany.SetLoanAmount(AICompany.GetMaxLoanAmount());
        local airport = AIAirport.AT_INTERCON;
        if (!AIAirport.IsValidAirportType(airport)) airport = AIAirport.AT_SMALL;
        local hangar = -1;
        for (local y=8; y<100 && hangar<0; y+=8) {
            for (local x=8; x<100 && hangar<0; x+=8) {
                local tile = AIMap.GetTileIndex(x,y);
                if (AIAirport.BuildAirport(tile, airport, AIStation.STATION_NEW)) hangar = AIAirport.GetHangarOfAirport(tile);
            }
        }
        Check(hangar >= 0, "build test airport");
        local passengers = -1;
        local mail = -1;
        foreach (cargo, unused in AICargoList()) if (AICargo.GetCargoLabel(cargo) == "PASS") passengers = cargo;
        foreach (cargo, unused in AICargoList()) if (AICargo.GetCargoLabel(cargo) == "MAIL") mail = cargo;
        foreach (p in expected) {
            local vehicle = AIVehicle.BuildVehicle(hangar, actual[p.name]);
            Check(AIVehicle.IsValidVehicle(vehicle), "build " + p.name);
            Check(AIVehicle.GetCapacity(vehicle, passengers) == p.capacity, "built capacity " + p.name);
            Check(AIVehicle.GetCapacity(vehicle, mail) == p.mail, "built mail compartment " + p.name);
            Check(AIVehicle.GetMaximumOrderDistance(vehicle) == p.range*p.range, "built range " + p.name);
            // Confirm that the distance API uses the same squared Euclidean metric.
            local diagonal = AIOrder.GetOrderDistance(AIVehicle.VT_AIR, AIMap.GetTileIndex(1,1), AIMap.GetTileIndex(4,5));
            Check(diagonal == 25, "aircraft distance metric");
            foreach (cargo, unused in AICargoList()) {
                if (!AIEngine.CanRefitCargo(actual[p.name], cargo)) continue;
                Check(AIVehicle.RefitVehicle(vehicle, cargo), "refit vehicle " + p.name);
                local label = AICargo.GetCargoLabel(cargo);
                local expected_capacity = label == "PASS" ? p.capacity : label == "MAIL" ? p.capacity+p.mail : label == "GOOD" ? (p.capacity+p.mail+1)/2 : (p.capacity+p.mail+2)/4;
                Check(AIVehicle.GetCapacity(vehicle, cargo) == expected_capacity, "refitted capacity " + p.name + ":" + label);
            }
            Check(AIVehicle.SellVehicle(vehicle), "sell " + p.name);
        }
'''


def squirrel(value):
    if isinstance(value, dict):
        return '{' + ','.join(f'{k}={squirrel(v)}' for k,v in value.items()) + '}'
    if isinstance(value, list):
        return '[' + ','.join(squirrel(v) for v in value) + ']'
    return json.dumps(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--openttd', type=Path, default=ROOT.parents[1]/'build/openttd')
    args = parser.parse_args()
    executable = args.openttd.resolve()
    game = ROOT / 'build/qa'
    for directory in ('newgrf', 'ai/NextGRFQA', 'scripts', 'home', 'save', 'config'):
        (game/directory).mkdir(parents=True, exist_ok=True)
    (game/'newgrf/nextgrf.grf').unlink(missing_ok=True)
    shutil.copy2(ROOT/'build/nextgrf.tar', game/'newgrf/nextgrf.tar')
    (game/'ai/NextGRFQA/info.nut').write_text(INFO)
    (game/'scripts/game_start.scr').write_text('start_ai "NextGRF QA"\n')
    defaults = default_aircraft()
    range_patches = {p['id']:p for p in default_ranges()}
    cases = [(1914,'temperate',False), (1940,'temperate',False),
             (2055,'temperate',True), (2055,'arctic',True),
             (2055,'tropic',True), (2055,'toyland',False)]
    summary = []
    for year, climate, build_checks in cases:
        expected = []
        for p in defaults + aircraft():
            if p['year'] > year or ('TOYLAND' in p['climates']) != (climate == 'toyland'):
                continue
            expected.append(dict(name=p['name'], capacity=p['passengers'], mail=p['mail'],
                                 speed=p['speed'], range=p['range'] if 'shape' in p else range_patches[p['id']]['range'], type=0 if p.get('helicopter') else 1 if p['small'] else 3,
                                 added='shape' in p, refits=p['refits']))
        script = SCRIPT.replace('EXPECTED', squirrel(expected)).replace('BUILD_CHECKS', BUILD_CHECKS if build_checks else '')
        (game/'ai/NextGRFQA/main.nut').write_text(script)
        cfg = game/'test.cfg'
        cfg.write_text(f'''[misc]
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
land_generator = 1
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
plane_speed = 4
[network]
server_port = 0
[newgrf]
nextgrf.tar/nextgrf/nextgrf.grf =
''')
        # Keep the global game scripts/profile out of the test search path. The
        # executable's own baseset directory supplies the mandatory extra GRF.
        bases = game/'baseset'
        if not bases.exists():
            bases.mkdir()
            for path in Path('/usr/share/games/openttd/baseset').iterdir():
                (bases/path.name).symlink_to(path, target_is_directory=path.is_dir())
        reference = bases/'opengfx2'
        if not reference.exists():
            reference.symlink_to(ensure_reference(), target_is_directory=True)
        import os
        environment = dict(os.environ, HOME=str(game/'home'), XDG_CONFIG_HOME=str(game/'config'), XDG_DATA_HOME=str(game/'home'))
        command = [str(executable), '-X', '-x', '-I', 'OpenGFX2 Classic', '-c', str(cfg), '-g', '-vnull:ticks=5000', '-snull', '-mnull', '-dscript=2,grf=0']
        # Compare stock capacities, speeds, costs, airport types and refit masks
        # with an actual no-GRF game, so a range patch cannot silently clone or
        # alter the other default aircraft properties.
        configured=cfg.read_text()
        cfg.write_text(configured.replace('nextgrf.tar/nextgrf/nextgrf.grf =',''))
        baseline_expected=[dict(p,range=0) for p in expected if not p['added']]
        (game/'ai/NextGRFQA/main.nut').write_text(SCRIPT.replace('EXPECTED',squirrel(baseline_expected)).replace('BUILD_CHECKS',''))
        baseline=subprocess.run(command,cwd=game,env=environment,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
        (game/f'{year}-{climate}-baseline.log').write_text(baseline.stdout)
        if baseline.returncode or 'NEXTGRF_QA_PASS' not in baseline.stdout:
            raise SystemExit(f'FAILED stock baseline {year} {climate}: {baseline.stdout[-4000:]}')
        cfg.write_text(configured)
        (game/'ai/NextGRFQA/main.nut').write_text(script)
        completed = subprocess.run(command, cwd=game, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60)
        log = completed.stdout
        log_path = game/f'{year}-{climate}.log'
        log_path.write_text(log)
        if completed.returncode or 'NEXTGRF_QA_PASS' not in log or 'NEXTGRF_QA_FAIL' in log:
            print(log[-10000:])
            raise SystemExit(f'FAILED {year} {climate}; see {log_path}')
        def snapshots(output):
            return {line.split('|',2)[1]:line.split('|',2)[2] for line in output.splitlines() if 'NEXTGRF_ENGINE|' in line}
        stock=snapshots(baseline.stdout);modified=snapshots(log)
        for name,properties in stock.items():
            if modified.get(name)!=properties:
                raise SystemExit(f'Range patch changed other stock properties: {name}: {properties} vs {modified.get(name)}')
        record = dict(year=year, climate=climate, aircraft=len(expected), stock_properties_compared=len(stock), build_refit_sell=build_checks, result='PASS')
        summary.append(record)
        print(record)
    (ROOT/'build/qa-results.json').write_text(json.dumps(summary, indent=2)+'\n')


if __name__ == '__main__':
    main()
