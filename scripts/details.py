"""Detailed research registers and geographic candidate matching."""
import math
import re
from collections import Counter, defaultdict
from shapely.geometry import shape, box, Point
from shapely.ops import transform
from pyproj import Transformer
from analyze import data, layers, key, norm, write, load

def props(f):
    return {k.lower(): str(v if v is not None else "").strip() for k,v in f["properties"].items()}

def semantic(p):
    # Direction retained; no merge on operator alone.
    return tuple(norm(p.get(k)) for k in ("nomempresa","nodo_1","nodo_2"))

def clock_class(s):
    n = norm(s)
    if n in {"","NA","N A","NO APLICA","SIN INFORMACION","NO REGISTRA","0"}:
        return "missing"
    if re.search(r"\b\d{1,2}[:.]\d{2}\b|\b\d{1,2}\s*(?:A\.?\s*M\.?|P\.?\s*M\.?)\b", s, re.I):
        return "clock_text"
    if re.search(r"\b(DIARIO|DIARIA|LUNES|MARTES|MIERCOLES|JUEVES|VIERNES|SABADO|DOMINGO|DIAS)\b", n):
        return "day_pattern"
    if re.search(r"\b(MINUTOS?|HORAS?)\b", n):
        return "interval_text"
    if re.search(r"DEMANDA|CUPO|LLENO", n):
        return "demand_text"
    return "other_text"

# Bounding rectangle deliberately includes the bay, nearby coast and lower Canal del Dique.
bounds = box(-75.75, 10.05, -75.30, 10.60)
project = Transformer.from_crs("EPSG:4326","EPSG:32618",always_xy=True).transform
sites = []
for f in load("infraestructura_no_concesionada"):
    if not f.get("geometry"):
        continue
    g = shape(f["geometry"])
    if g.geom_type != "Point" or g.is_empty:
        continue
    p = props(f)
    sites.append((p, transform(project,g)))
ops = defaultdict(lambda: {"names":set(),"passenger":0,"tourism":0})
routes, candidates, spatial = [], [], []
classes = Counter()
thematic = defaultdict(list)
for category, layer in [("passenger",layers[1]),("tourism",layers[3])]:
    seen = set()
    for f in data[layer]:
        k = key(f)
        if k in seen:
            continue
        seen.add(k)
        p = props(f)
        oid = p.get("id") or str(f.get("id","")) or p.get("fid","")
        rid = layer + ":" + str(len(routes)+1)
        operator = norm(p.get("nomempresa"))
        if operator:
            ops[operator]["names"].add(p.get("nomempresa",""))
            ops[operator][category] += 1
        a,b = p.get("nodo_1",""),p.get("nodo_2","")
        t,fr = p.get("horario",""),p.get("frecuencia","")
        tc,fc = clock_class(t),clock_class(fr)
        classes[category,tc,fc] += 1
        g = shape(f["geometry"]) if f.get("geometry") else None
        hit = g is not None and not g.is_empty and g.intersects(bounds)
        direct = "CARTAGENA" in (norm(a),norm(b))
        context = any("CARTAGENA" in norm(p.get(x)) for x in ("zoperac","municipio","insfluvial"))
        row = dict(route_id=rid,source_id=oid,source_layer=layer,category=category,operator_key=operator,
            operator=p.get("nomempresa",""),department=p.get("departamen",""),municipality=p.get("municipio",""),
            origin=a,destination=b,timetable=t,frequency=fr,timetable_class=tc,frequency_class=fc,
            spatial_cartagena=bool(hit),name_match="endpoint" if direct else "context_only" if context else "")
        routes.append(row)
        if hit or direct or context:
            spatial.append(row)
        sk = semantic(p)
        if all(sk):
            thematic[sk].append(rid)
        if g is None or g.is_empty:
            continue
        lines = [g] if g.geom_type == "LineString" else list(g.geoms) if g.geom_type == "MultiLineString" else []
        if not lines:
            continue
        # Geometry order is not assumed to be the operational direction.
        for label, coord in [("geometry_start",lines[0].coords[0]),("geometry_end",lines[-1].coords[-1])]:
            pt = transform(project,Point(coord[:2]))
            nearby = sorted(((pt.distance(loc),site) for site,loc in sites),key=lambda x:x[0])
            for distance,site in nearby[:3]:
                if distance > 1000:
                    continue
                candidates.append(dict(route_id=rid,geometry_endpoint=label,site_id=site.get("objectid",""),
                    site_name=site.get("nom_infra",""),site_municipality=site.get("municipio",""),
                    site_status=site.get("estado_actual_o_i",""),distance_m=round(distance),status="candidate_only"))

fields = ["route_id","source_id","source_layer","category","operator_key","operator","department","municipality","origin","destination","timetable","frequency","timetable_class","frequency_class","spatial_cartagena","name_match"]
write("routes.csv",fields,routes)
write("cartagena_routes.csv",fields,spatial)
write("operators.csv",["operator_key","source_names","passenger_records","tourism_records"],[
    dict(operator_key=k,source_names=" | ".join(sorted(v["names"])),passenger_records=v["passenger"],tourism_records=v["tourism"]) for k,v in sorted(ops.items())])
write("schedule_classes.csv",["category","timetable_class","frequency_class","records"],[
    dict(category=c,timetable_class=t,frequency_class=f,records=n) for (c,t,f),n in sorted(classes.items())])
write("landing_candidates.csv",["route_id","geometry_endpoint","site_id","site_name","site_municipality","site_status","distance_m","status"],candidates)
comparison=[]
for i,f in enumerate(data[layers[0]]):
    p=props(f)
    sk=semantic(p)
    matches=thematic.get(sk,[]) if all(sk) else []
    comparison.append(dict(general_index=i+1,source_id=p.get("id",""),operator=p.get("nomempresa",""),
        origin=p.get("nodo_1",""),destination=p.get("nodo_2",""),candidate_count=len(matches),
        thematic_route_ids=" | ".join(matches),status="unique_candidate" if len(matches)==1 else "ambiguous" if matches else "unmatched"))
write("general_layer_comparison.csv",["general_index","source_id","operator","origin","destination","candidate_count","thematic_route_ids","status"],comparison)
write("general_layer_fields.csv",["field"],[{"field":k} for k in sorted({k for f in data[layers[0]] for k in props(f)})])
print("Detailed routes:",len(routes),"operators:",len(ops),"Cartagena spatial matches:",sum(r["spatial_cartagena"] for r in routes),"landing candidates:",len(candidates))
print("General layer candidate statuses:",Counter(r["status"] for r in comparison))
