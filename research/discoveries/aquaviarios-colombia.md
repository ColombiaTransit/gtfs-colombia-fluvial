# Manual discovery: Transportes Aquaviarios de Colombia SAS

Recorded 2026-11-24 from a Supertransporte route popup supplied by the user. Cross-checked against the existing `rutas_fluvial_turismo.geojson` (st04), source record id 18. The supplied business identifier is intentionally not reproduced in this public repository, consistent with the existing NIT exclusion policy.

## Observed registration

- Operator: Transportes Aquaviarios de Colombia SAS
- Modality: Turismo
- Department: Cordoba
- Municipality: Monteria
- Node 1: Monteria
- Node 2: San Bernardo del Viento
- Direction: Redondo
- Vessel type: Bote
- Fluvial inspection: blank in user-supplied popup
- Operating zone: Rio Sinu, Cienagas de Ayapel, Betanci, Lorica y la Represa de Urra
- Timetable and frequency: blank in stored source

## Other registrations in the same stored layer

| Source id | Department | Node 1 | Node 2 |
|---|---|---|---|
| 13 | Atlantico | Barranquilla | Puente Laureano Goméz |
| 14 | Atlantico | Cartagena | Calamar |
| 15 | Atlantico | Barranquilla | Cartagena |
| 16 | Atlantico | Circular laguna | Circular laguna |
| 17 | Antioquia | Circular embalse | Circular embalse |
| 18 | Cordoba | Monteria | San Bernardo del Viento |

All six are tourism registrations with blank timetable and frequency fields. Operating-zone descriptions do not establish intermediate stops. The Córdoba discovery is already present in the dataset, not an additional seventh route.

## Follow-up

Deferred: investigate operator identity, authorizations, current operations, landing sites and whether any service is suitable for GTFS. No current public scheduled service has been confirmed.

## Sources

- [Supertransporte tourism FeatureServer](https://chamaeleon.supertransporte.gov.co/gisserver/rest/services/Hosted/Rutas_Fluvial_Turismo/FeatureServer/0)
- [Stored tourism layer](../../data/processed/supertransporte/rutas_fluvial_turismo.geojson)
- User-supplied popup transcription, 2026-11-24; exact route viewer URL not independently established.

## Additional manual discovery: Cartagena – Calamar

Recorded 2026-11-24 from a user-supplied Supertransporte route popup. Matches the existing tourism registration st04, source record id 14.

- Operator: Transportes Aquaviarios de Colombia SAS
- Fluvial inspection: Cartagena (as displayed in the popup)
- Modality: Turismo
- Department: Atlantico
- Municipality: Barranquilla
- Node 1: Cartagena
- Node 2: Calamar
- Direction: Redondo
- Vessel type: Bote
- Operating zone: Rio Magdalena desde Barranquilla hasta Puerto Salgar y Canal del Dique hasta Cartagena
- Timetable and frequency: blank in the stored source

The supplied NIT matches the identifier in the earlier user-supplied Córdoba popup; it is not reproduced in the public repository. The department and municipality are registration attributes, not necessarily the route origin. This is not an additional route or proof of current scheduled operation. Keep separate from the regular passenger registration Cartagena–Calamar attributed to Transportes del Mar SAS.
