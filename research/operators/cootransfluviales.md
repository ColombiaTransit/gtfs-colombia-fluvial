# Batch 1 — Cootransfluviales Unidos Ltda

Reviewed 2026-11-24. [Resolution 20233040027545 of 2023-07-04](https://www.cootransfluviales.com/doc/RESOLUCION%20PERMISO%20DE%20OPERACION%20TRANS%20DE%20PASAJEROS%2020233040027545.pdf), page 6, Article 3, was visually inspected. Nine connections and both directions are authorized, all daily, with intermediate ports explicitly mentioned but not individually listed. Article 4 provides a three-year term from executoria; exact effective date and subsequent renewal not established. Do not assume current authorization or publish a feed yet. The source PDF is linked rather than copied (contains identifiers; redistribution review pending).

The companion CSV preserves the schedule punctuation (slash marks a line break). Hyphens may separate departures or time windows; two-token rows need confirmation. Cantagallo is circular in both rows; do not model simultaneous independent departures without evidence. Older GeoJSON differs for Puerto Berrio, San Pablo (old times match reverse direction), and Simiti. Prefer the 2023 legal schedule as historical evidence, subject to renewal and operational confirmation.

All nine have source line geometries. Orientation candidates come from endpoint locations, not observed sailing direction. Cerro Burgos and Simiti share candidate site 680; do not merge or assume road transfer without confirmation. El Banco and Cantagallo nearest candidates are inactive. San Pablo and San Rafael lack a destination candidate. Puerto Berrio has an active San Bartolo candidate and another main-port candidate; verify actual boarding. Water alignment and durations are still unverified.

Sources checked:
- https://cootransfluviales.com/ — operator describes passenger service and Yuma terminal opening hours (not departures).
- https://www.barrancabermeja.gov.co/directorio/30/empresas-fluviales/ — municipal directory lists operator.
- https://cootransfluviales.com/Rutas2.html — route/fare image index; date unknown.
- https://cootransfluviales.com/img/ruta1.jpg — Barrancabermeja fare image, intermediate destinations and candidate fares (e.g. El Banco 100000 COP, Puerto Berrio 43000 COP, Gamarra not verified here, Cerro de Burgos 62000 COP, Cantagallo 28000 COP, San Pablo 37000 COP). Not a stop sequence or current fare confirmation.
- https://cootransfluviales.com/img/ruta6.jpg — Puerto Berrio fare image, Barrancabermeja 43000 COP.
- https://www.cootransfluviales.com/Documentos_1.html — search index lists permit but live retrieval returned unrelated spam; treat domain content cautiously and verify via ministry.

Next: find 2026 renewal, verify fares and actual intermediate stops, compare shapes against OSM water geometry, obtain sailing durations. No newer permit found in this search round. No operator contacted.
