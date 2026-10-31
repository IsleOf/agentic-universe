# Civilian disaster observation: satellite-data constraints

**Reviewed:** 2026-11-01. This note concerns disaster situational awareness for civilian rescue and inspection. It does not validate automatic dispatch, navigation, or any aircraft.

## Candidate observations

- **Observation age is not product latency.** NASA defines FIRMS latency relative to satellite observation; polar-orbiting satellites do not continuously cover all locations. Waiting for an observation must be considered separately from processing and delivery.[1]
- **A thermal detection is not a complete fire boundary.** NASA distinguishes active-fire detections from fire-perimeter mapping. Satellite observations sample particular times, and cloud cover can obscure polar-orbiting observations.[1]
- **Missing detection does not prove absence.** An observation may be unavailable because the location is between overpasses or obscured by clouds; geostationary products also have coarse spatial resolution and potentially inconsistent accuracy.[1]
- **Rapid Mapping is not instantaneous.** Copernicus describes emergency-mapping products as taking hours to days and using suitable satellite imagery and other geospatial inputs. Products and their imagery have specific observation times; publication is not the same event as acquisition.[2][3]
- **Resolution and refresh are separate properties.** Copernicus identifies multiple imagery resolution classes used in its emergency products. The appropriate imagery and its age must be evaluated for the question, rather than assuming all maps support close-range identification.[4]

## Proposed knowledge-graph candidates

All entries below are **`to_test`** project hypotheses, not validated systems or proven edges:

1. `observation_age_vs_product_latency`: distinguish acquisition time, dissemination time, and time since incident; test stale-observation handling against timestamped examples.[1][3]
2. `thermal_anomaly_is_not_perimeter`: preserve detection semantics, sensor footprint and uncertainty; compare with authoritative incident information where available.[1]
3. `missing_detection_is_not_clearance`: represent unknown/occluded observations separately from negative findings.[1]
4. `emergency_map_provenance`: retain source product, observation time, publication/update time, resolution class and revision.[2][3][4]

A relationship from an observation to a mission decision is a proposed analytical connection, not an independently tested integration. Source age, interpretation, human review, and separate operational safety checks matter before any real-world action.

## Scope and data-access check

A public Copernicus activation metadata request returned HTTP 200 and two activation summaries on 2026-11-01. This confirms that endpoint returned metadata at that moment; it does not measure imagery acquisition, product availability, API reliability, or operational end-to-end response time. No personal data, accounts, or export were accessed.

## Sources

[1] https://ntrs.nasa.gov/api/citations/20260004514/downloads/FIRMS%20Inform%20Wildfire.pdf
[2] https://mapping.emergency.copernicus.eu/about/rapid-mapping-portfolio
[3] https://mapping.emergency.copernicus.eu/about/rapid-mapping-manual/product-overview/what-is-a-product
[4] https://mapping.emergency.copernicus.eu/about/using-of-earth-observation-data
