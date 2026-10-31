# NextGRF

NextGRF 0.4.0 adds **253 vehicles from 1700 to 2050** to OpenTTD's default fleet:
20 aircraft, 24 locomotives, 115 wagons, 25 ships, 14 buses and 55 cargo road
vehicles. It extends the familiar fictional manufacturers across more eras,
including eight generations of rail wagons and cargo road vehicles.
All 41 default aircraft also receive finite flight ranges.
Only their range property is changed; other default properties and OpenTTD's
C++ source remain unchanged.

## Install and play

Copy `build/nextgrf.tar` into your active profile's `newgrf` folder. On a default
Linux profile that is `~/.local/share/openttd/newgrf/`. Install OpenGFX2 Classic
through Online Content or put its release tar in the profile's `baseset` folder.

In OpenTTD, select **OpenGFX2 Classic** in Game Options > Graphics. In the main
menu, open NewGRF Settings, rescan files if necessary, add **NextGRF**, and apply.
Start a new game. Restarting OpenTTD can refresh its base-set list. Installing a
file does not change a running save's NewGRF list.

Start in 1700 for sailing ships, 1804 for the first railway, 1886 for buses,
1896 for cargo trucks, or 1914 for aircraft. Use 2055 to try the future models
after the game's randomized introduction period. To inspect all
historical vehicles simultaneously, enable Vehicles never expire before creating
the game. No special airports or other NewGRFs are required. Keep the default
multiple-NewGRF-vehicle-sets / dynamic-engines setting enabled.

NextGRF adds vehicles in Temperate, Arctic and Tropical climates. Livestock
vehicles are limited to Temperate and Arctic. Toyland remains
without new vehicles, but its default aircraft receive finite ranges too.
Other vehicle NewGRFs can change the default roster or global cost
bases independently; use NextGRF alone for the catalog's intended comparison.

## Build

Requirements: Python 3.12+ (the reference extractor uses safe tar extraction),
Pillow and NML 0.8+. Ubuntu's `nml` package supplies the compiler and Pillow.
No GRFCodec, Blender, PDF library, CMake changes or OpenTTD rebuild is needed.
The merged PDF catalog uses `pdfunite` from Poppler (`poppler-utils` on Ubuntu).

```sh
make                  # sprites, NML, .grf, .tar and checksums
make catalog          # aircraft, rail and surface PDFs, previews and JSON
make check            # vehicle-ID and sprite checks
make test             # build, checks and real aircraft/rail/surface NoAI games
make install          # install both packages in your current user's data profile
```

The catalog and integration checks fetch a pinned OpenGFX2 Classic 0.8.1 release
on first use, verify its SHA-256, and cache it under `build/reference/`. The
playable set itself does not require that download to compile. Set
`OPENTTD=/absolute/path/to/openttd` for another executable. The integration checks
use isolated configurations and run no multiplayer server. They do not run the
OpenTTD repository's deferred regression suite.

Outputs:

- `build/nextgrf.grf`: playable NewGRF, GRFID `NXTA`, integer version 4.
- `build/nextgrf.tar`: installable package with documentation and GPL license.
- `build/nextgrf-source.tar.gz`: complete corresponding source and artwork study.
- `build/NextGRF-Catalog.pdf`: all 41 default and 20 NextGRF aircraft, identified
  as **DEFAULT** or **NEXTGRF**, with all eight headings and gameplay settings.
- `build/NextGRF-Rail-Catalog.pdf`: all 116 default + 139 NextGRF rail entries.
- `build/NextGRF-Surface-Catalog.pdf`: all 99 default + 94 NextGRF surface entries.
- `build/NextGRF-Full-Catalog.pdf`: the three catalogs in one volume.
- `build/{fleet,rail,surface}-preview.png`: sprite contact sheets.
- `build/nextgrf.nml`, `build/*roster.json`: compiled definitions and full data.
- `build/default-aircraft-ranges.json`: range-only patches and service roles for
  all 41 original aircraft; the catalog shows effective and stock ranges.
- `build/sprites/`: native 1x, 2x and 4x atlases for every vehicle, with empty
  and loaded stages for trains, ships and road vehicles.
- `build/*catalog-data.json`, `build/*qa-results.json`: comparison and test data.

## Edit the set

`tools/roster.py` is the vehicle data source, including fixed IDs 64-83, all
properties, comparison models and each aircraft's geometry family and size.
Never change a released model's ID or reuse a removed ID. `tools/render.py`
defines the editable aircraft meshes, orthographic camera, shading and palette.
`tools/rail.py` and `tools/surface.py` define the other fleets; their associated
`*_render.py` and `*_nml.py` files define geometry and compiler properties.
`tools/build.py` generates the NML and language file. `lang/english.lng` contains
aircraft names and shared descriptions; other names come from the rosters.
Rebuild after changes. IDs are permanent within each vehicle feature.

Artwork is original DOS-palette pixel art. Every vehicle has eight consistent
headings at native 1x, 2x and 4x resolutions (11,664 compiled sprites).
Aircraft use primary company colours. Other vehicles use primary and secondary
company colours. Rail and surface meshes include cargo load stages where visible.
The earlier AI-generated styling study
is kept in `assets/concepts/` for provenance; it is not used as game sprites.

## Gameplay properties

Every model specifies introduction date, supported climates, manufacturer support
period, individual vehicle life, retirement offset, reliability decay, loading
speed, cargo ageing, purchase/running cost factors, airport class, speed,
acceleration, passenger/mail capacity, finite range, refit rules and sound.
All fields are included in the catalog or machine-readable roster. This release
has no user parameters. Wagons, ships and road vehicles use literal capacity
callbacks to retain their native-unit capacity across refits.

### Railways and wagon generations

The 24 locomotives progress from the Kirby Paul Pioneer in 1804 through steam,
diesel and electric traction to X3000 monorail, Lev5 Griffin maglev and the SH 90
in 2050. Default locomotives remain available on their original schedules.
New locomotives use the standard RAIL, ELRL, MONO and MGLV track types.

| Generation | Year | Passengers | Mail | Bulk | Passenger km/h | Freight km/h |
| --- | --- | --- | --- | --- | --- | --- |
| G1 | 1804 | 8 | 10 | 4 | 25 | 20 |
| G2 | 1835 | 16 | 16 | 8 | 60 | 45 |
| G3 | 1870 | 28 | 24 | 14 | 100 | 70 |
| G4 | 1920 | 40 | 32 | 22 | 140 | 100 |
| G5 | 1960 | 56 | 40 | 32 | 180 | 120 |
| G6 | 1990 | 64 | 50 | 42 | 230 | 140 |
| G7 | 2020 | 80 | 65 | 52 | 280 | 160 |
| G8 | 2040 | 96 | 80 | 64 | 320 | 200 |

Nine families cover passengers, mail, bulk, covered goods, liquids, flat loads,
livestock, refrigerated cargo and valuables. Refrigerated rail vans begin in G3;
secure and livestock capacity is three quarters of the bulk reference. Mail
shares the passenger speed limit. Keep **Wagon speed limits** enabled in Settings
to enforce the configured wagon speeds.

Monorail has G6-G8 wagons, available from 1998, with passenger speed limits of
360/420/480 km/h and freight limits of 180/210/240. Maglev has G7-G8 from 2020,
with passenger limits of 660/720 and freight limits of 280/320. Capacities match
their conventional rail generation. Conventional wagons also run on ELRL.

Generation IDs are separate. Existing vehicles keep their original capacity,
speed and appearance; buying or autoreplacing with a newer model upgrades the
fleet. Purchase windows overlap; G8 and endgame locomotives never expire from
the purchase list. Wagons have no separate running cost, following the default
economic model. Powered passenger modules carry passengers and can haul coaches.

### Ships and road vehicles

Ships begin in 1700 and progress through sailing packets and merchantmen, paddle
steamers, ocean liners, tankers, container carriers and fast ferries to 2050.
Ferries refit between passengers and mail in a **single compartment**, tankers
carry liquid cargoes, and cargo ships accept dry cargo classes. Later cargo ships
run at 60% ocean speed in canals; later ferries use 75%. Early ships use 100%.
Sailing rigs and electric propulsion use standard ship physics.

Buses start with the 12-passenger MPS Steam Omnibus in 1886. The late fleet offers
large city buses, a 150-passenger double-decker and faster electric coaches.
Cargo trucks have eight generations (1896, 1915, 1935, 1955, 1975, 1995, 2020,
2040), progressing from 3 to 50 native cargo units and 24 to 140 km/h. Covered
vans also refit to mail. Other bodies carry bulk, liquids, flat loads, livestock,
refrigerated cargo and valuables. Refrigerated trucks begin in G2. These are
ordinary single road vehicles, with no special roads or charging infrastructure.

### Aircraft

All models refit to passengers, mail, goods and the climate's valuables cargo.
Guru Galaxy II/III additionally carry food. Only cargos present in the selected
climate are offered. The standard aircraft refit rules apply: mail capacity is
passengers + mail, goods is half the sum, and valuables/food is a quarter, rounded
to the nearest integer. Passenger configurations have a separate mail compartment.
Refitting is free. Primary company colours and the game's normal aircraft shadows
are used; no second-company-colour flag is needed.

The Coleman Courier is a mail-heavy aircraft with **40 passengers + 40 bags of
mail** in its standard configuration. A full mail refit carries 80 bags.

### Flight ranges

Every NextGRF addition has a finite range, measured as straight-line distance
between airports in **map tiles per flight leg**, not kilometres or a total
fuel budget. Intermediate airport stops permit longer multi-leg routes. The
range applies regardless of refit. Default aircraft now have finite ranges too,
including the default helicopters and Toyland aircraft. These patches define
**only** the range property on original aircraft IDs 0-40; names, sprites,
capacities, dates, costs, refits and other properties remain inherited.

Flight ranges are explicit gameplay settings in `tools/ranges.py`, grouped by
service role. The LB-12 has **512 tiles**, Yate Z-Shuttle II **318**, and Coleman
Count IV **250**. Airtaxi A35 has **1,485**, Darwin 650 **1,504**, and Airtaxi A37
**1,589** tiles. Large long-haul additions span **1,051-1,589** tiles; regional
jets, turboprops, early aircraft and helicopters have shorter missions.

The hybrid Coleman Count E trades range (**130**) for lower running costs.
Supersonic aircraft also trade range for speed: FFP Hyperdart 3 has **812**.
These values are game balance choices, not real-world specifications.

Default examples: Sampson U52 **183**, Darwin 100 **512**, Darwin 300 **1,354**,
Darwin 600 **1,429**, Dinger 200 **1,504**, Tricario Helicopter **81**. The catalog
lists every default and NextGRF range and its service role. Default entries are
marked DEFAULT and record that their stock range was unlimited.

NML range documentation:
https://newgrf-specs.tt-wiki.net/wiki/NML:Vehicles#Aircraft_properties .

Aircraft speeds are quantized to the engine's native steps. The catalog states
the requested values for NextGRF and approximate displayed values for defaults.
Introduction dates can be randomized by up to 511 days and include a preview
period. Money values depend on currency, inflation and cost settings; raw factors
allow fair comparisons without inventing fixed prices. Default aircraft also
inherit the game's aircraft speed setting, as do these additions.

Historical aircraft have finite manufacturer support periods. Endgame models
include a turboprop, a small jet, widebodies and a supersonic aircraft that never
expire from the purchase list. Their individual vehicles still age. Future
propulsion technologies are fictional economic/visual themes, with standard
game mechanics. Balance is an initial playable pass, not a claim of completed
long-term economic playtesting.

## License and reference material

Original NextGRF code and rendered vehicle sprites are GPL-2.0; see `LICENSE`
and `CREDITS.md`. Default OpenGFX2 vehicle art is used only in the comparison
catalog. It is not copied into the playable GRF. The source remains available
alongside this build in this directory. `NXTA` is a project-local GRFID; check
for public-registry collisions before distributing through BaNaNaS.
