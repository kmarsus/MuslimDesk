"""One-off: build assets/data/world_cities.json (country -> top cities) from
the offline geonamescache package (bundled data, no network needed), so the
app's country/city picker works fully offline. Top 20 cities by population
per country, plus the capital if it wasn't already in that set.
"""
import json
from pathlib import Path

import geonamescache

gc = geonamescache.GeonamesCache()
countries = gc.get_countries()
cities = gc.get_cities()

by_country: dict[str, list[dict]] = {code: [] for code in countries}
for c in cities.values():
    code = c.get("countrycode")
    if code in by_country:
        by_country[code].append(c)

result = {}
for code, country in sorted(countries.items(), key=lambda kv: kv[1]["name"]):
    country_cities = sorted(by_country.get(code, []), key=lambda c: -c.get("population", 0))
    top = country_cities[:20]
    capital = country.get("capital", "")
    if capital and not any(c["name"] == capital for c in top):
        cap_match = next((c for c in country_cities if c["name"] == capital), None)
        if cap_match:
            top.append(cap_match)
    if not top:
        continue
    result[code] = {
        "name": country["name"],
        "cities": [
            {
                "name": c["name"],
                "lat": round(c["latitude"], 4),
                "lon": round(c["longitude"], 4),
                "timezone": c["timezone"],
            }
            for c in sorted(top, key=lambda c: c["name"])
        ],
    }

out = Path(r"C:\Claude\MuslimDesk\assets\data\world_cities.json")
out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Wrote {len(result)} countries, {sum(len(v['cities']) for v in result.values())} cities -> {out}")
