import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "ml" / "landslide_model.joblib"

FEATURES = [
    "rainfall24", "rainfall72", "soil", "slope",
    "elevation", "ndvi", "road_dist", "history",
]

LABELS = ["LOW", "MODERATE", "HIGH"]

def _load_model():
    if not MODEL_PATH.exists():
        from ml.train import train
        train()
    return joblib.load(MODEL_PATH)

MODEL = _load_model()

def predict(features: dict):
    x = pd.DataFrame([{k: float(features[k]) for k in FEATURES}])
    proba = MODEL.predict_proba(x)[0]

    # Hazard probability mapped to an intuitive 0–100 score.
    score = float(proba[1] * 50 + proba[2] * 100)

    if score >= 72:
        level = "CRITICAL"
    elif score >= 52:
        level = "HIGH"
    elif score >= 30:
        level = "MODERATE"
    else:
        level = "LOW"

    # Entropy-based uncertainty proxy: more concentrated probabilities = higher confidence.
    entropy = -float(np.sum(proba * np.log(proba + 1e-9)))
    confidence = float(np.clip(1 - entropy / np.log(len(proba)), 0, 1))

    # Exposure proxy for operational prioritization.
    exposure = float(np.clip(
        0.55 * (1 - features["road_dist"] / 1500)
        + 0.30 * features["history"] / 12
        + 0.15 * features["soil"] / 100, 0, 1
    ) * 100)

    # Hazard x exposure. This is deliberately separate from hazard probability.
    priority = float(np.clip(0.65 * score + 0.35 * exposure, 0, 100))

    importances = MODEL.feature_importances_
    names = [
        "24h rainfall", "72h rainfall", "soil moisture", "slope",
        "elevation", "vegetation", "road proximity", "historical density"
    ]
    explanations = sorted(
        [{"factor": n, "importance": round(float(v), 4)}
         for n, v in zip(names, importances)],
        key=lambda z: z["importance"], reverse=True
    )

    if level == "CRITICAL":
        action = "Immediate field verification + district control-room escalation"
    elif level == "HIGH":
        action = "Increase patrol frequency + prepare targeted warning"
    elif level == "MODERATE":
        action = "Enhanced monitoring + validate sensor readings"
    else:
        action = "Routine monitoring"

    return {
        "risk_level": level,
        "risk_score": round(score, 2),
        "confidence": round(confidence, 3),
        "exposure_score": round(exposure, 2),
        "operational_priority": round(priority, 2),
        "probabilities": {
            "LOW": round(float(proba[0]), 4),
            "MODERATE": round(float(proba[1]), 4),
            "HIGH": round(float(proba[2]), 4),
        },
        "top_factors": explanations[:5],
        "recommended_action": action,
        "model_version": "LG-NER-RF-1.0",
    }
