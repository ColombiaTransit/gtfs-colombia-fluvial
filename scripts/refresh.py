"""Fetch selected FeatureServer layers into temporary local copies for analysis."""
import csv
import json
import tempfile
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]

def query(url, **params):
    with urlopen(url + "/query?" + urlencode({"f": "json", **params}), timeout=90) as r:
        result = json.load(r)
    if "error" in result:
        raise RuntimeError(result["error"])
    return result

def refresh(row):
    url = row["source_url"]
    ids = query(url, where="1=1", returnIdsOnly="true")
    object_ids = sorted(ids["objectIds"])
    if not object_ids or len(set(object_ids)) != len(object_ids):
        raise RuntimeError("Empty or duplicate object IDs: " + url)
    features = []
    for start in range(0, len(object_ids), 100):
        params = dict(objectIds=",".join(map(str, object_ids[start:start+100])),
                      outFields="*", returnGeometry="true", outSR=4326, f="geojson")
        with urlopen(url + "/query?" + urlencode(params), timeout=90) as r:
            result = json.load(r)
        if result.get("type") != "FeatureCollection" or result.get("exceededTransferLimit"):
            raise RuntimeError("Incomplete GeoJSON response: " + url)
        chunk = result["features"]
        if len(chunk) != len(object_ids[start:start+100]):
            raise RuntimeError("Feature count mismatch: " + url)
        for feature in chunk:
            # Remove identifiers not needed by the aggregate analysis.
            feature["properties"] = {k:v for k,v in feature["properties"].items()
                if not any(x in k.lower() for x in ("nit", "email", "correo", "telefono", "editor", "creator", "usuario"))}
        features.extend(chunk)
    path = ROOT / row["processed_path"]
    path.write_text(json.dumps({"type":"FeatureCollection","features":features}, ensure_ascii=False), encoding="utf-8")
    print(row["source_id"], len(features))

with (ROOT / "research/sources.csv").open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["source_id"] in {"st01","st02","st03","st04","st05"}:
            refresh(row)
