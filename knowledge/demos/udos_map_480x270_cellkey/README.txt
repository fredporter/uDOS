APAC-centred 480×270 Cell Reference Pack
========================================

Grid & Projection
-----------------
- Grid: 480 columns × 270 rows (16×16 px cells)
- Centre longitude: 120°E (APAC in the middle)
- Longitude span: 360° total mapped so 120°E is at grid column ~240
- Latitude span: +85° to −85° (uniform per-row mapping)

Cell Codes
----------
- Column codes: spreadsheet-style A, B, …, Z, AA, AB, … up to RL
- Row codes: 1..270
- A1-style cell reference: e.g., "CR128" means column CR, row 128 (1-based)

Conversions
-----------
- APAC wrap for longitude: lon' = wrap(lon − 120°) into [−180°, +180°)
- Column index: col = floor( (lon' + 180°) / 360° * 480 )
- Row index:    row = floor( (85° − lat) / 170° * 270 )

Workflow
--------
1) Put your city list into data/cities.csv (or extend cities_sample.csv).
   Required columns: city, country, lat, lon, code3
2) Run tools/compute_keys.py to generate output/key.csv with CellCode and indices.
3) On the ASCII map, render each city as: '*' and put the 3–4 letter label nearby.
4) Print or render the side key listing City • Country • Code • CellCode.

Included
--------
- tools/compute_keys.py — CLI script to convert lat/lon → cell codes
- data/cities_sample.csv — ~70 cities as a seed (expand to 200+ as needed)
- output/key_example.csv — computed cell codes for the sample

Tips for 200+ Cities
--------------------
- Use short labels (IATA-like): NYC, LON, DEL, TYO, SYD, JKT, MNL, DXB, CAI, LOS, SAO, MEX.
- Enforce min spacing (e.g., ≥6 cols × 3 rows) to avoid collision.
- Ocean anchoring + leader lines help fit dense regions (Europe, East China).
- Consider two density modes: Top-100 and Top-250 (toggle on/off).
