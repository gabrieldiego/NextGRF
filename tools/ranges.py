"""Finite flight ranges in map tiles per airport-to-airport leg.

Values are explicit gameplay settings. Stable vehicle IDs and all non-range
properties are managed by the aircraft roster and the default definitions.
"""

# Aircraft key: (range in map tiles, service role).
AIRCRAFT_RANGES = {
    'sampson_u12': (44, 'Pioneer light transport'),
    'bakewell_lb1': (73, 'Early cabin airliner'),
    'sampson_u26': (110, 'Early trimotor airliner'),
    'coleman_courier': (293, 'Passenger and mail transport'),
    'coleman_count2': (146, 'Early regional turboprop'),
    'coleman_count3': (225, 'Regional turboprop'),
    'guru_galaxy2': (1051, 'Long-haul trijet'),
    'coleman_count4': (250, 'Modern regional turboprop'),
    'darwin_650': (1504, 'Long-haul widebody'),
    'airtaxi_a35': (1485, 'Long-haul widebody'),
    'bakewell_lb12': (512, 'Short/medium-haul rear-engine jet'),
    'yate_zshuttle2': (318, 'Regional jet'),
    'coleman_counte': (130, 'Short-range regional transport'),
    'airtaxi_a36': (1559, 'Future long-haul widebody'),
    'kelling_k2': (332, 'Mail-heavy regional jet'),
    'guru_galaxy3': (1208, 'Heavy passenger and mail transport'),
    'ffp_hyperdart3': (812, 'Supersonic express'),
    'dinger_300': (1579, 'Long-haul jumbo'),
    'airtaxi_a37': (1589, 'Future long-haul airliner'),
    'darwin_800': (1579, 'Future long-haul airliner'),
}


# Original feature-local ID, stock name, range in map tiles, service role.
# These entries patch only range; stock artwork and other properties are inherited.
DEFAULT_RANGES = [
    (0, 'Sampson U52', 183, 'Early light passenger transport'),
    (1, 'Coleman Count', 130, 'Early regional turboprop'),
    (2, 'FFP Dart', 460, 'Early medium-range jet'),
    (3, 'Yate Haugan', 643, 'Early supersonic express'),
    (4, 'Bakewell Cotswald LB-3', 146, 'Small piston airliner'),
    (5, 'Bakewell Luckett LB-8', 1051, 'Early long-haul jet'),
    (6, 'Bakewell Luckett LB-9', 384, 'Short-haul rear-engine jet'),
    (7, 'Bakewell Luckett LB80', 945, 'Older long-haul narrowbody'),
    (8, 'Bakewell Luckett LB-10', 409, 'Domestic rear-engine jet'),
    (9, 'Bakewell Luckett LB-11', 460, 'Updated domestic rear-engine jet'),
    (10, 'Yate Aerospace YAC 1-11', 332, 'Short-haul regional jet'),
    (11, 'Darwin 100', 512, 'Medium-range narrowbody'),
    (12, 'Darwin 200', 449, 'Short/medium-haul narrowbody'),
    (13, 'Darwin 300', 1354, 'Early long-haul jumbo'),
    (14, 'Darwin 400', 757, 'Extended-range narrowbody'),
    (15, 'Darwin 500', 1156, 'Long-haul twin-engine widebody'),
    (16, 'Darwin 600', 1429, 'Long-haul twin-engine widebody'),
    (17, 'Guru Galaxy', 1051, 'Three-engine widebody'),
    (18, 'Airtaxi A21', 1051, 'Early widebody'),
    (19, 'Airtaxi A31', 998, 'Medium/long-haul widebody'),
    (20, 'Airtaxi A32', 561, 'Medium-haul narrowbody'),
    (21, 'Airtaxi A33', 1337, 'Long-haul twin-engine widebody'),
    (22, 'Yate Aerospace YAe46', 250, 'Regional turboprop mission'),
    (23, 'Dinger 100', 318, 'Regional jet'),
    (24, 'AirTaxi A34-1000', 289, 'Small regional jet'),
    (25, 'Yate Z-Shuttle', 289, 'Four-engine regional jet'),
    (26, 'Kelling K1', 260, 'Small regional jet'),
    (27, 'Kelling K6', 318, 'Regional jet'),
    (28, 'Kelling K7', 486, 'Medium-range high-mail jet'),
    (29, 'Darwin 700', 617, 'Medium-haul high-mail narrowbody'),
    (30, 'FFP Hyperdart 2', 677, 'Supersonic express'),
    (31, 'Dinger 200', 1504, 'Long-haul jumbo'),
    (32, 'Dinger 1000', 1116, 'Future long-range supersonic express'),
    (33, 'Ploddyphut 100', 146, 'Toyland light propeller transport'),
    (34, 'Ploddyphut 500', 162, 'Toyland regional propeller transport'),
    (35, 'Flashbang X1', 404, 'Toyland regional jet'),
    (36, 'Juggerplane M1', 1051, 'Toyland large jet'),
    (37, 'Flashbang Wizzer', 744, 'Toyland supersonic express'),
    (38, 'Tricario Helicopter', 81, 'Local helicopter shuttle'),
    (39, 'Guru X2 Helicopter', 125, 'Extended-range helicopter shuttle'),
    (40, 'Powernaut Helicopter', 81, 'Toyland helicopter shuttle'),
]


def set_range(plane):
    distance, role = AIRCRAFT_RANGES[plane['key']]
    plane.update(range=distance, range_role=role)


def default_ranges():
    return [dict(id=identifier, name=name, range=distance, range_role=role)
            for identifier, name, distance, role in DEFAULT_RANGES]
