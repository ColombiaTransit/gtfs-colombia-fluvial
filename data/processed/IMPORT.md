# Initial geographic imports

Nine GeoJSON datasets were parsed from the user-provided exports and feature counts checked before upload. The five route layers retain 1,500 source registrations, not 1,500 unique routes. No deduplication was applied during import.

The public copies omit NIT fields from route layers and concession ports, and editor account identifiers from concession ports and pilot boarding points. Original source snapshots remain pending; these copies are not byte-identical originals. Other source attributes and geometries were retained through JSON parsing and serialization. Redistribution terms have not been independently confirmed. The DIMAR Excel exports remain pending and are not represented as uploaded data. Pilot boarding points are reference data only, not passenger stops.

Source URLs and counts: `research/sources.csv`.
