# Production Roadmap

## Phase 1 — Pilot
- Collect validated historical landslide inventory.
- Integrate approved rainfall feed.
- Install/ingest calibrated soil-moisture and tilt sensors.
- Build DEM-derived slope/aspect/curvature features.
- Establish baseline performance metrics.

## Phase 2 — Remote sensing
- Sentinel-1 deformation / InSAR pipeline.
- Sentinel-2 vegetation and land-cover change.
- Raster/vector spatial joins in PostGIS.

## Phase 3 — ML maturity
- XGBoost baseline.
- Temporal sequence model if sufficient labels exist.
- Probability calibration.
- uncertainty estimation.
- spatial/temporal cross-validation.
- model drift monitoring.

## Phase 4 — Operations
- FastAPI services behind authentication.
- PostGIS.
- message queue.
- object storage.
- offline-first Android field app.
- role-based access.
- alert approval workflow.
- monitoring and audit logs.

## Success metrics
- precision/recall for high-risk events
- lead time before confirmed events
- false-alert rate
- calibration error
- field verification turnaround
- percentage of critical assets covered
- system uptime and offline synchronization success
