"""One-off: convert city_data.dart (coords + Bangla names) into cities_bd.json."""
import json
import re
from pathlib import Path

SRC = Path(r"C:\Claude\app-IOM-Daily-Azkar\lib\core\constants\city_data.dart")
DST = Path(r"C:\Claude\MuslimDesk\assets\data\cities_bd.json")

text = SRC.read_text(encoding="utf-8")

coord_re = re.compile(r"'([^']+)':\s*Coordinates\(([-\d.]+),\s*([-\d.]+)\)")
name_re = re.compile(r"'([^']+)':\s*'([^']+)'")

coords_block = text[text.index("cityMap = {"):text.index("class CityNamesBN")]
names_block = text[text.index("cityNamesBN = {"):]

coords = {m.group(1): (float(m.group(2)), float(m.group(3))) for m in coord_re.finditer(coords_block)}
names = {m.group(1): m.group(2) for m in name_re.finditer(names_block)}

cities = []
for key, (lat, lon) in coords.items():
    if key == "Selected City":
        continue
    cities.append({
        "key": key,
        "name_bn": names.get(key, key),
        "lat": lat,
        "lon": lon,
    })

cities.sort(key=lambda c: c["key"])
DST.write_text(json.dumps(cities, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {len(cities)} cities to {DST}")
