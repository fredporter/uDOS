#!/usr/bin/env python3
import csv, sys, math, argparse

COLS, ROWS = 480, 270
LON_CENTRE = 120.0
LAT_MAX, LAT_MIN = 85.0, -85.0

def wrap_lon(lon):
    shifted = lon - LON_CENTRE
    while shifted < -180.0:
        shifted += 360.0
    while shifted >= 180.0:
        shifted -= 360.0
    return shifted

def lon_to_col(lon):
    x = (wrap_lon(lon) + 180.0) / 360.0 * COLS
    return max(0, min(COLS-1, int(math.floor(x))))

def lat_to_row(lat):
    y = (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * ROWS
    return max(0, min(ROWS-1, int(math.floor(y))))

def col_to_letters(col0):
    n = col0 + 1
    letters = ""
    while n > 0:
        n, rem = divmod(n-1, 26)
        letters = chr(65 + rem) + letters
    return letters

def cell_code(col0, row0):
    return f"{col_to_letters(col0)}{row0+1}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=True, help="Input CSV with city,country,lat,lon,code3")
    ap.add_argument("--out", dest="outfile", required=True, help="Output CSV with cell codes")
    args = ap.parse_args()

    with open(args.infile, "r", encoding="utf-8") as fi, open(args.outfile, "w", newline="", encoding="utf-8") as fo:
        r = csv.DictReader(fi)
        w = csv.writer(fo)
        w.writerow(["city","country","code3","lat","lon","col_index0","row_index0","cell_code"])
        for row in r:
            city = row["city"]
            country = row["country"]
            lat = float(row["lat"])
            lon = float(row["lon"])
            code3 = row.get("code3","")
            col = lon_to_col(lon)
            rowi = lat_to_row(lat)
            w.writerow([city, country, code3, lat, lon, col, rowi, cell_code(col, rowi)])

if __name__ == "__main__":
    main()
