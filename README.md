# Colombia Fluvial Transit

Research, source inventories and future GTFS generation for inland waterway passenger transport in Colombia.

## Scope

Nationwide research, organized by river basin and operational network. Cartagena Lanchas remains a separate maritime project. Shared source inventories may support both projects.

## Repository structure

- `data/raw/`: immutable source snapshots, subject to redistribution and privacy review.
- `data/processed/`: normalized and deduplicated datasets.
- `research/`: source, route, operator, landing site, timetable, fare and evidence registers.
- `docs/`: methodology and quality documentation.
- `scripts/`, `tests/`: reproducible processing and validation.

## Principles

Official registrations are evidence, not proof of current operation. Small operators need not have websites; local observations and official authorities are valid evidence. Distinguish scheduled departures, operating windows, demand-responsive service and service days. Avoid double counting shared operations. Preserve original identifiers and source wording. Do not invent missing travel times or stops.

No GTFS feed is published yet. Regional feeds will follow data validation with the MobilityData GTFS validator.

See `research/sources.csv` and `research/worklist.csv` for progress.
