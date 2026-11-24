"""Build reproducible research summaries from committed geographic imports."""
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

def norm(value):
    return re.sub(r"[^A-Z0-9]+", " ", "".join(c for c in unicodedata.normalize("NFKD", str(value or "").upper()) if not unicodedata.combining(c))).strip()

def write(name, fields, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def load(name):
    p = ROOT / "data" / "processed" / "supertransporte" / (name + ".geojson")
    return json.loads(p.read_text(encoding="utf-8"))["features"]

def key(feature):
    p = {k.lower(): v for k, v in feature["properties"].items()}
    # Ignore publication-specific row identifiers; retain substantive attributes and geometry.
    p = {k: v for k, v in p.items() if k not in {"fid", "objectid", "globalid", "shape__length", "shape_length"}}
    return json.dumps([p, feature.get("geometry")], sort_keys=True, ensure_ascii=False)

layers = ["rutas_pax_etf", "rutas_fluvial_pasajeros", "etf_pasajeros_27122022", "rutas_fluvial_turismo", "etf_turismo_27122022"]
data = {name: load(name) for name in layers}
keys = {name: set(map(key, features)) for name, features in data.items()}
write("layer_summary.csv", ["layer", "records", "distinct_exact_records"], [
    dict(layer=n, records=len(data[n]), distinct_exact_records=len(keys[n])) for n in layers])
write("layer_overlap.csv", ["layer_a", "layer_b", "exact_common_records"], [
    dict(layer_a=a, layer_b=b, exact_common_records=len(keys[a] & keys[b]))
    for i, a in enumerate(layers) for b in layers[i+1:]])

# Use one thematic publication per category; avoid counting mirrored layers twice.
# The general and alternate layers are audited separately above, not silently merged.
operators = defaultdict(lambda: {"names": set(), "passenger": 0, "tourism": 0})
regions = Counter()
coverage = Counter()
routes = []
for category, layer in [("passenger", layers[1]), ("tourism", layers[3])]:
    seen = set()
    for feature in data[layer]:
        k = key(feature)
        if k in seen:
            continue
        seen.add(k)
        p = {k.lower(): v for k, v in feature["properties"].items()}
        def val(k):
            return str(p.get(k) or "").strip()
        name = val("nomempresa")
        operator = norm(name)
        if operator:
            operators[operator]["names"].add(name)
            operators[operator][category] += 1
        department = norm(val("departamen"))
        municipality = norm(val("municipio"))
        regions[category, department, municipality] += 1
        origin, destination = val("nodo_1"), val("nodo_2")
        timetable, frequency = val("horario"), val("frecuencia")
        coverage[category, bool(timetable), bool(frequency)] += 1
        # Explicit name match only, not a spatial intersection; flag broad zone matches separately.
        endpoint = any(norm(x) == "CARTAGENA" for x in (origin, destination))
        zone = any("CARTAGENA" in norm(x) for x in (val("zoperac"), municipality, val("insfluvial")))
        routes.append(dict(category=category, source_layer=layer, source_id=val("id"), operator=name,
            department=department, municipality=municipality, origin=origin, destination=destination,
            timetable=timetable, frequency=frequency, operating_zone=val("zoperac"),
            cartagena_match="endpoint" if endpoint else "context_only" if zone else ""))
fields = ["category","source_layer","source_id","operator","department","municipality","origin","destination","timetable","frequency","operating_zone","cartagena_match"]
# Do not publish individual source timetable text or operator names until redistribution review.
write("regional_summary.csv", ["category","department","municipality","records"], [
    dict(category=c, department=d, municipality=m, records=n) for (c,d,m),n in sorted(regions.items())])
write("timetable_coverage.csv", ["category","timetable_nonblank","frequency_nonblank","records"], [
    dict(category=c,timetable_nonblank=t,frequency_nonblank=f,records=n) for (c,t,f),n in sorted(coverage.items())])
write("operator_summary.csv", ["category","distinct_normalized_names","records_with_name"], [
    dict(category=c, distinct_normalized_names=sum(v[c]>0 for v in operators.values()), records_with_name=sum(v[c] for v in operators.values())) for c in ("passenger","tourism")] +
    [dict(category="combined",distinct_normalized_names=len(operators),records_with_name=sum(v["passenger"]+v["tourism"] for v in operators.values()))])
write("cartagena_summary.csv", ["category","match_type","records"], [
    dict(category=c,match_type=m,records=n) for (c,m),n in sorted(Counter((r["category"],r["cartagena_match"]) for r in routes if r["cartagena_match"]).items())])
print("Distinct normalized operator names:", len(operators))
print("Thematic distinct records:", len(routes))
