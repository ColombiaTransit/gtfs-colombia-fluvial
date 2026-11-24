# Generated research summaries

Run `python scripts/analyze.py` or the Fluvial research analysis workflow. The workflow commits aggregate CSV results directly to main; no Actions artifacts are created.

The optional refresh input fetches five Supertransporte route layers in batches by object ID, requests WGS84 GeoJSON, and checks returned feature counts. Refreshed source copies remain temporary on the runner and are not committed pending redistribution review. DIMAR Excel exports and offshore pilot boarding points are outside automated refresh scope.

Counts use the passenger and tourism thematic layers, with exact within-layer deduplication. Alternate publications and the general layer are compared independently in the overlap matrix. Exact comparison ignores publication row IDs but may miss semantically equivalent records. Operator counts normalize spelling punctuation, case and accents; they are not legal-entity counts. Nonblank timetable fields are not validated schedules. Cartagena context matches can include unrelated places such as Punta Cartagena; they are not spatial matches. Detailed registers are derived from existing published research copies; they contain selected business names and operational fields only, not NITs or contact fields. Redistribution terms remain unverified.

## Detailed analysis

Run `python scripts/details.py` with Shapely and pyproj installed. It also generates the aggregate outputs. Cartagena spatial selection uses a provisional rectangle (longitude -75.75 to -75.30, latitude 10.05 to 10.60) and keeps name-only matches separately. Landing candidates are the nearest three recorded infrastructure points within 1 km of each geometry endpoint (UTM zone 18N); they are not verified passenger stops or operational directions. General-layer matching uses normalized operator and ordered endpoints, and is a candidate comparison, not proof of equivalence. Schedule classification is heuristic, not a GTFS timetable. Route IDs are research row identifiers, not stable GTFS IDs.
