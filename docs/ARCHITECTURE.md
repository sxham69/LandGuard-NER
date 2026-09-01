# System Architecture

```text
 ┌──────────────────────────────────────────────────────────────┐
 │                     NER DATA FABRIC                          │
 │ IMD • IoT • DEM • Sentinel-1 • Sentinel-2 • GIS • Reports │
 └─────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Data Quality +       │
                    │ Feature Engineering  │
                    └──────────┬───────────┘
                               ▼
                    ┌──────────────────────┐
                    │ AI RISK ENGINE       │
                    │ Random Forest v1     │
                    │ + uncertainty       │
                    └──────────┬───────────┘
                               │
               ┌───────────────┼────────────────┐
               ▼               ▼                ▼
        Hazard score      Explainability   Confidence
               │               │                │
               └───────────────┼────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │ IMPACT ENGINE        │
                    │ roads • settlements  │
                    │ critical assets      │
                    └──────────┬───────────┘
                               ▼
                    OPERATIONAL PRIORITY
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
       GIS MAP            DIGITAL TWIN          ALERTS
          │                    │                    │
          └──────────────┬─────┴──────────────┬─────┘
                         ▼                    ▼
                 FIELD VERIFICATION      AUDIT LOG
                         │
                         ▼
                  LABELED DATA LOOP
                         │
                         └──────► MODEL RETRAINING
```

## Key design decision

Hazard and impact are intentionally separated.

A remote slope with high hazard but no exposed asset may deserve monitoring. A similar hazard adjacent to a strategic road or dense settlement can receive higher operational priority.

This makes the platform more useful to a control room than a single risk map.
