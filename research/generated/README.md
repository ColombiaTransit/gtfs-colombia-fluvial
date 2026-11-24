# Generated research summaries

Run `python scripts/analyze.py` or the Fluvial research analysis workflow. The workflow commits aggregate CSV results directly to main; no Actions artifacts are created.

The optional refresh input fetches five Supertransporte route layers in batches by object ID, requests WGS84 GeoJSON, and checks returned feature counts. Refreshed source copies remain temporary on the runner and are not committed pending redistribution review. DIMAR Excel exports and offshore pilot boarding points are outside automated refresh scope.

Counts use the passenger and tourism thematic layers, with exact within-layer deduplication. Alternate publications and the general layer are compared independently in the overlap matrix. Exact comparison ignores publication row IDs but may miss semantically equivalent records. Operator counts normalize spelling punctuation, case and accents; they are not legal-entity counts. Nonblank timetable fields are not validated schedules. Cartagena context matches can include unrelated places such as Punta Cartagena; they are not spatial matches. Individual route and operator registers are deferred pending redistribution review.
