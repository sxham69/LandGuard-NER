from datetime import datetime, timedelta
import numpy as np
import pandas as pd

DISTRICTS = [
    {"district":"Aizawl","state":"Mizoram","lat":23.7271,"lon":92.7176},
    {"district":"Gangtok","state":"Sikkim","lat":27.3389,"lon":88.6065},
    {"district":"Shillong","state":"Meghalaya","lat":25.5788,"lon":91.8933},
    {"district":"Itanagar","state":"Arunachal Pradesh","lat":27.0844,"lon":93.6053},
    {"district":"Kohima","state":"Nagaland","lat":25.6751,"lon":94.1086},
    {"district":"Imphal","state":"Manipur","lat":24.8170,"lon":93.9368},
    {"district":"Agartala","state":"Tripura","lat":23.8315,"lon":91.2868},
    {"district":"Guwahati","state":"Assam","lat":26.1445,"lon":91.7362},
]

def district_features(seed: int):
    rng = np.random.default_rng(seed)
    return {
        "rainfall24": float(rng.uniform(15, 120)),
        "rainfall72": float(rng.uniform(45, 280)),
        "soil": float(rng.uniform(35, 92)),
        "slope": float(rng.uniform(15, 48)),
        "elevation": float(rng.uniform(400, 2100)),
        "ndvi": float(rng.uniform(.35, .85)),
        "road_dist": float(rng.uniform(40, 600)),
        "history": float(rng.uniform(.2, 7)),
    }

def all_zones():
    out = []
    for i, d in enumerate(DISTRICTS):
        row = dict(d)
        row["features"] = district_features(26001 + i)
        out.append(row)
    return out

def sensor_stream(hours=24, seed=42):
    rng = np.random.default_rng(seed)
    now = datetime.now().replace(second=0, microsecond=0)
    times = [now - timedelta(minutes=5*i) for i in range(hours*12)][::-1]
    return pd.DataFrame({
        "timestamp": times,
        "rainfall_mm_h": np.maximum(0, rng.normal(12, 6, len(times))),
        "soil_moisture_pct": np.clip(rng.normal(64, 8, len(times)), 25, 95),
        "tilt_deg": np.maximum(0, rng.normal(.7, .3, len(times))),
    })

def exposure_assets():
    return pd.DataFrame([
        {"asset":"NH-6 corridor","type":"Strategic road","district":"Shillong","exposure":92,"lat":25.58,"lon":91.89},
        {"asset":"Aizawl hillside road","type":"Road","district":"Aizawl","exposure":88,"lat":23.73,"lon":92.72},
        {"asset":"Gangtok access corridor","type":"Strategic road","district":"Gangtok","exposure":94,"lat":27.34,"lon":88.61},
        {"asset":"Itanagar hillside settlements","type":"Settlement","district":"Itanagar","exposure":82,"lat":27.08,"lon":93.61},
        {"asset":"Shillong urban slope","type":"Settlement","district":"Shillong","exposure":86,"lat":25.57,"lon":91.90},
    ])
