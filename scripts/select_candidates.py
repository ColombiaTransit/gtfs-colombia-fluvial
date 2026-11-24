"""Prioritize routes with schedule evidence; research output only, not a GTFS feed."""
import csv
import re
from collections import Counter, defaultdict
from math import isfinite
from pyproj import Geod
from shapely.geometry import shape
from details import routes, candidates, data, layers, key, props, norm, write
from analyze import ROOT

GEOD = Geod(ellps="WGS84")
DAY_NAMES = ("LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO")
DAY_CODES = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
# Explicit regional research buckets, not inferred hydrological basin boundaries.
NETWORKS = {
    "COOTRANSFLUVIALES": "Magdalena corridor",
    "COOTRAGAM": "Magdalena corridor",
    "TRANSPORTADORA SAN PABLO LIMITADA": "Magdalena corridor",
    "COOTRAFLUCAP": "Magdalena corridor",
    "COOTRAIMAG": "Magdalena corridor",
    "COOTRAFLUVSUC": "La Mojana",
    "COOMULTRAMAG": "Magdalena corridor",
    "TRANSMARYRIO": "Atrato - Uraba",
    "TRANSPORTE FLUVIAL MIXTO ATRATO CARIBE RIO BAUDO": "Atrato - Uraba",
    "TRANSNUEVO LLORO SAS": "Atrato - Uraba",
    "COOTRANSFLUMAR": "Atrato - Uraba",
    "COOTRANSPUERTO ASIS LTDA": "Putumayo",
    "COOTRANSPIÑUÑA": "Putumayo",
    "COOTRANS PINUNA": "Putumayo",
    "EXPRESO LIBERTADOR LIMITADA": "Putumayo - Caqueta (review)",
}
NETWORKS = {norm(k): v for k, v in NETWORKS.items()}

def schedule(t, f):
    # Extract only well-formed 24-hour tokens. Keep all source strings and
    # distinguish time lists from prose, intervals and ambiguous two-time ranges.
    tokens = re.findall(r"(?<!\d)([01]?\d|2[0-3])[:.]([0-5]\d)(?!\d)", t)
    times = [f"{int(h):02d}:{m}" for h, m in tokens]
    n = norm(t + " " + f)
    pure = bool(re.fullmatch(r"\s*\d{1,2}[:.]\d{2}(?:\s*[-,;/]\s*\d{1,2}[:.]\d{2})*\s*", t))
    raw_tokens = re.findall(r"\d{1,2}[:.]\d{2}", t)
    if re.search(r"\b(DEMANDA|CUPO|LLENO|INTERDIARIO|ALTERNA\w*|CONTINUA|CADA)\b", n):
        ts = "operational_pattern_review"
    elif not times or len(raw_tokens) != len(times) or not pure:
        ts = "clock_text_review"
    elif len(times) == 2:
        ts = "two_times_review"
    elif times != sorted(set(times)):
        ts = "ordering_review"
    else:
        ts = "single_time" if len(times) == 1 else "time_list"
    fn = norm(f)
    if fn in {"DIARIA","DIARIO","TODOS LOS DIAS","LUNES A DOMINGO","LUNES A DOMINGOS"}:
        days, ds = list(DAY_CODES), "daily"
    elif re.search(r"\b(INTERDIARIO|ALTERNA\w*|MEDIO|CADA|DEMANDA)\b", fn):
        days, ds = [], "alternating_or_other_review"
    else:
        names = fn.replace("VIERMES","VIERNES")
        words = names.split()
        if words and all(w in DAY_NAMES or w in {"Y","LOS"} for w in words) and any(w in DAY_NAMES for w in words):
            days, ds = [code for day,code in zip(DAY_NAMES,DAY_CODES) if day in words], "explicit_days"
        else:
            days, ds = [], "missing" if not fn else "day_text_review"
    return "|".join(times), ts, "|".join(days), ds

def geometry_info(f):
    result = dict(shape_status="missing",geometry_type="",shape_points=0,shape_length_km="",parts=0,max_part_gap_m="",geometry_start="",geometry_end="")
    if not f.get("geometry"):
        return result
    try:
        g = shape(f["geometry"])
        result["geometry_type"] = g.geom_type
        lines = [g] if g.geom_type == "LineString" else list(g.geoms) if g.geom_type == "MultiLineString" else []
        if not lines or g.is_empty:
            result["shape_status"] = "not_linear"
            return result
        coords = [list(l.coords) for l in lines if not l.is_empty]
        if not coords or any(len(a)<2 for a in coords) or any(not (isfinite(x) and isfinite(y) and -180<=x<=180 and -90<=y<=90) for a in coords for x,y,*_ in a):
            result["shape_status"] = "invalid_coordinates"
            return result
        length = sum(GEOD.line_length([p[0] for p in a],[p[1] for p in a]) for a in coords)
        gaps = [GEOD.inv(a[-1][0],a[-1][1],b[0][0],b[0][1])[2] for a,b in zip(coords,coords[1:])]
        result.update(shape_status="line_candidate" if g.is_valid and length>0 and len(coords)==1 else "multipart_or_invalid_review",
                      shape_points=sum(map(len,coords)),shape_length_km=round(length/1000,3),parts=len(coords),
                      max_part_gap_m=round(max(gaps,default=0),1),
                      geometry_start=f"{coords[0][0][1]:.7f}|{coords[0][0][0]:.7f}",
                      geometry_end=f"{coords[-1][-1][1]:.7f}|{coords[-1][-1][0]:.7f}")
    except (ValueError, TypeError, AttributeError) as e:
        result["shape_status"]="geometry_error"
    return result

# Match the same deduplication and row order as details.py; assert source identity.
features = {}
i = 0
for layer in (layers[1],layers[3]):
    seen = set()
    for f in data[layer]:
        k = key(f)
        if k in seen:
            continue
        seen.add(k)
        i += 1
        features[f"{layer}:{i}"] = f
assert len(features)==len(routes)
near = defaultdict(list)
for x in candidates:
    near[x["route_id"],x["geometry_endpoint"]].append(x)

selected, shapes, stops, queue = [], [], [], []
for r in routes:
    if r["category"]!="passenger" or r["timetable_class"]!="clock_text":
        continue
    rid = r["route_id"]
    f = features[rid]
    p = props(f)
    assert norm(p.get("nomempresa")) == r["operator_key"]
    assert p.get("nodo_1","") == r["origin"] and p.get("nodo_2","") == r["destination"]
    geo = geometry_info(f)
    times, ts, days, ds = schedule(r["timetable"],r["frequency"])
    best = {}
    for endpoint in ("geometry_start","geometry_end"):
        options = sorted(near[rid,endpoint], key=lambda x: (x["distance_m"],x["site_id"]))
        if options:
            best[endpoint] = options[0]
        for rank,x in enumerate(options,1):
            stops.append(dict(**x,rank=rank,within_250m=x["distance_m"]<=250))
    both = all(e in best and best[e]["distance_m"]<=250 for e in ("geometry_start","geometry_end"))
    distinct = both and bool(best["geometry_start"]["site_id"]) and bool(best["geometry_end"]["site_id"]) and best["geometry_start"]["site_id"]!=best["geometry_end"]["site_id"]
    days_known = ds in {"daily","explicit_days"}
    times_clean = ts in {"single_time","time_list"}
    priority = "A" if days_known and times_clean and distinct and geo["shape_status"]=="line_candidate" else "B" if r["frequency_class"]=="day_pattern" and geo["shape_status"]=="line_candidate" else "C"
    network = NETWORKS.get(r["operator_key"], "Unassigned: "+(r["department"] or "unknown"))
    selected.append(dict(**r,departure_tokens=times,time_status=ts,service_days=days,day_status=ds,
                         direction_source=p.get("sentido",""),operating_zone=p.get("zoperac",""),
                         network=network,priority=priority,shape_status=geo["shape_status"],
                         both_endpoints_250m=both,distinct_sites_250m=distinct,
                         start_distance_m=best.get("geometry_start",{}).get("distance_m",""),
                         end_distance_m=best.get("geometry_end",{}).get("distance_m","")))
    shapes.append(dict(route_id=rid,source_id=r["source_id"],shape_source=r["source_layer"],**geo,
                       operational_direction="unverified",water_alignment="unverified"))
    issues = ["confirm_current_operation","confirm_travel_duration","confirm_direction_and_return_service","confirm_passenger_stops"]
    if not times_clean: issues.append("interpret_timetable")
    if not days_known: issues.append("interpret_service_days")
    if geo["shape_status"]!="line_candidate": issues.append("review_shape_or_find_osm")
    if not distinct: issues.append("resolve_landing_sites")
    if both and any(norm(best[e]["site_status"])!="ACTIVA" for e in best): issues.append("check_landing_status")
    if network.startswith("Unassigned:"): issues.append("assign_network")
    for issue in issues:
        queue.append(dict(route_id=rid,operator=r["operator"],network=network,priority=priority,task=issue,status="open"))
selected.sort(key=lambda r:(r["priority"],r["network"],r["operator_key"],r["route_id"]))
ops = defaultdict(list)
nets = defaultdict(list)
for r in selected:
    ops[r["operator_key"]].append(r)
    nets[r["network"]].append(r)
def summary(items):
    return dict(routes=len(items),priority_a=sum(r["priority"]=="A" for r in items),
                priority_b=sum(r["priority"]=="B" for r in items),priority_c=sum(r["priority"]=="C" for r in items),
                both_endpoints_250m=sum(r["both_endpoints_250m"] for r in items),
                distinct_sites_250m=sum(r["distinct_sites_250m"] for r in items))
operator_rows = [dict(operator_key=k,operator=" | ".join(sorted({r["operator"] for r in v})),networks=" | ".join(sorted({r["network"] for r in v})),**summary(v)) for k,v in ops.items()]
operator_rows.sort(key=lambda r:(-r["priority_a"],-r["both_endpoints_250m"],-r["routes"],r["operator_key"]))
network_rows = [dict(network=k,operators=len({r["operator_key"] for r in v}),**summary(v)) for k,v in sorted(nets.items())]
def output(name,rows,fields=None):
    write(name,fields or list(rows[0]),rows)
output("candidate_routes.csv",selected)
output("candidate_operators.csv",operator_rows)
output("candidate_shapes.csv",shapes)
output("candidate_stops.csv",stops)
output("candidate_networks.csv",network_rows)
# External leads stay separate until rechecked; do not duplicate the source population.
with (ROOT/"research"/"external_schedule_leads.csv").open(encoding="utf-8",newline="") as f:
    external=list(csv.DictReader(f))
for e in external:
    for task in ("recheck_published_schedule","compare_existing_operator_and_route","confirm_service_days_and_duration","validate_shape_and_landing_sites"):
        queue.append(dict(route_id=e["lead_id"],operator=e["operator"],network=e["network"],priority="external",task=task,status="open"))
output("research_queue.csv",queue)
assert len(selected)==len(shapes)
assert sum(r["routes"] for r in operator_rows)==len(selected)
assert sum(r["routes"] for r in network_rows)==len(selected)
print("Candidate selection:",summary(selected),"operators:",len(ops),"external leads:",len(external))
