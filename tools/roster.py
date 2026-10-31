"""The single source of truth for NextGRF's aircraft and editable geometry.

IDs are deliberately above the 41 default aircraft slots. Never reuse a released ID.
Prices are multipliers of OpenTTD's aircraft base costs, not fixed currency values.
"""

from ranges import set_range

VERSION = 4
RELEASE = '0.4.0'
GRFID = "NXTA"  # Private project identifier; check public registry before publishing.
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
IDS = {
    'sampson_u12': 64, 'bakewell_lb1': 65, 'sampson_u26': 66,
    'coleman_courier': 67, 'coleman_count2': 68, 'coleman_count3': 69,
    'guru_galaxy2': 70, 'coleman_count4': 71, 'darwin_650': 72,
    'airtaxi_a35': 73, 'bakewell_lb12': 74, 'yate_zshuttle2': 75,
    'coleman_counte': 76, 'airtaxi_a36': 77, 'kelling_k2': 78,
    'guru_galaxy3': 79, 'ffp_hyperdart3': 80, 'dinger_300': 81,
    'airtaxi_a37': 82, 'darwin_800': 83,
}

# key, display name, year, pax, mail, km/h, purchase factor, running factor,
# small airport compatible, vehicle life, model life, loading speed,
# geometry family, length in normal-zoom pixels, default comparison model.
# Finite ranges and their benchmark proportions are defined in tools/ranges.py.
ROWS = [
    ("sampson_u12", "Sampson U12", 1914, 2, 2, 120, 2, 2, True, 12, 18, 4, "biplane", 17, "Sampson U52"),
    ("bakewell_lb1", "Bakewell Cotswald LB-1", 1919, 8, 3, 180, 4, 10, True, 15, 20, 6, "cabin_biplane", 23, "Bakewell Cotswald LB-3"),
    ("sampson_u26", "Sampson U26", 1924, 14, 4, 280, 7, 25, True, 18, 22, 8, "trimotor", 26, "Sampson U52"),
    ("coleman_courier", "Coleman Courier", 1938, 40, 40, 475, 14, 80, True, 22, 25, 16, "piston", 31, "Coleman Count"),
    ("coleman_count2", "Coleman Count II", 1958, 60, 10, 600, 16, 90, True, 24, 28, 18, "turboprop", 33, "Coleman Count"),
    ("coleman_count3", "Coleman Count III", 1976, 72, 12, 650, 17, 95, True, 25, 30, 20, "long_turboprop", 35, "Yate Aerospace YAe46"),
    ("guru_galaxy2", "Guru Galaxy II", 1990, 280, 50, 950, 29, 205, False, 28, 32, 28, "trijet", 48, "Guru Galaxy"),
    ("coleman_count4", "Coleman Count IV", 2005, 80, 14, 650, 19, 90, True, 26, 30, 22, "high_turboprop", 36, "AirTaxi A34-1000"),
    ("darwin_650", "Darwin 650", 2008, 300, 45, 950, 32, 205, False, 28, 32, 30, "widebody", 49, "Darwin 600"),
    ("airtaxi_a35", "Airtaxi A35", 2015, 280, 35, 950, 30, 175, False, 28, 32, 30, "winglet_jet", 47, "Airtaxi A33"),
    ("bakewell_lb12", "Bakewell Luckett LB-12", 2024, 190, 25, 950, 23, 140, False, 28, 32, 26, "rearjet", 39, "Bakewell Luckett LB-11"),
    ("yate_zshuttle2", "Yate Z-Shuttle II", 2028, 95, 15, 950, 20, 125, True, 25, 35, 24, "regional_quad", 34, "Yate Z-Shuttle"),
    ("coleman_counte", "Coleman Count E", 2032, 70, 12, 650, 23, 65, True, 25, None, 24, "electric", 34, "Coleman Count"),
    ("airtaxi_a36", "Airtaxi A36", 2035, 320, 40, 950, 36, 170, False, 30, 35, 34, "longwing", 50, "Airtaxi A35"),
    ("kelling_k2", "Kelling K2", 2038, 90, 30, 950, 24, 115, True, 26, None, 26, "canard", 33, "Kelling K1"),
    ("guru_galaxy3", "Guru Galaxy III", 2040, 360, 70, 950, 42, 215, False, 30, None, 38, "freighter", 53, "Guru Galaxy II"),
    ("ffp_hyperdart3", "FFP Hyperdart 3", 2043, 150, 35, 2330, 90, 250, False, 25, None, 26, "delta", 54, "FFP Hyperdart 2"),
    ("dinger_300", "Dinger 300", 2046, 480, 80, 950, 60, 250, False, 30, None, 42, "doubledeck", 59, "Dinger 200"),
    ("airtaxi_a37", "Airtaxi A37", 2050, 360, 45, 950, 48, 165, False, 30, None, 40, "blended", 48, "Airtaxi A36"),
    ("darwin_800", "Darwin 800", 2050, 240, 65, 950, 38, 155, False, 30, None, 34, "joined", 46, "Darwin 700"),
]

FIELDS = ("key", "name", "year", "passengers", "mail", "speed", "cost_factor",
          "running_cost_factor", "small", "vehicle_life", "model_life", "loading_speed",
          "shape", "length", "comparison")

def aircraft():
    result = []
    for row in ROWS:
        item = dict(zip(FIELDS, row))
        set_range(item)
        item.update(id=IDS[item['key']], reliability_decay=20, retire_early=0,
                    acceleration=18 if row[2] < 1930 else (25 if row[8] else 40),
                    refit_cost=0, cargo_age_period=185,
                    refits=["PASS", "MAIL", "GOOD", "VALU", "GOLD", "DIAM"],
                    climates=["TEMPERATE", "ARCTIC", "TROPICAL"])
        if item["shape"] in ("trijet", "freighter"):
            item["refits"].append("FOOD")
        item["sound"] = ("SOUND_TAKEOFF_JET_FAST" if item["shape"] == "delta" else
                         "SOUND_TAKEOFF_PROPELLER" if item["shape"] in
                         ("biplane", "cabin_biplane", "trimotor", "piston", "turboprop",
                          "long_turboprop", "high_turboprop", "electric") else "SOUND_TAKEOFF_JET")
        result.append(item)
    return result
