from datetime import datetime
import json
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db, insert_incident, insert_alert, insert_prediction, rows, UPLOAD_DIR
from backend.data_engine import all_zones, sensor_stream, exposure_assets
from backend.risk_engine import predict
from backend.incident_ai import analyze_image
from backend.notification_service import dispatch_email, mobile_push_status, send_email

app = FastAPI(
    title="LandslideGuard NER API",
    version="1.0.0",
    description="AI decision-support API for landslide risk monitoring."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


@app.post("/email/send")
def email_send(payload: dict):
    to = str(payload.get("to", "")).strip()
    message = str(payload.get("message", "")).strip()
    subject = str(payload.get("subject", "LandslideGuard NER Alert")).strip()
    if not to or not message:
        return {"status": "FAILED", "error": "Both 'to' and 'message' are required."}
    return send_email(to, subject, message)

@app.get("/health")
def health():
    return {"status":"online","service":"LandslideGuard NER","version":"1.0.0"}

@app.get("/zones")
def zones():
    out = []
    for z in all_zones():
        prediction = predict(z["features"])
        row = {k:v for k,v in z.items() if k != "features"}
        row.update(prediction)
        insert_prediction((
            datetime.now().isoformat(timespec="seconds"),
            row["district"], row["risk_level"], row["risk_score"],
            row["confidence"], row["exposure_score"],
            row["operational_priority"], json.dumps(z["features"])
        ))
        out.append(row)
    return out

@app.post("/predict")
def prediction(payload: Dict[str, Any]):
    return predict(payload)

@app.get("/sensors")
def sensors():
    df = sensor_stream()
    return df.to_dict(orient="records")

@app.get("/assets")
def assets():
    return exposure_assets().to_dict(orient="records")

@app.get("/incidents")
def incidents():
    return rows("incidents")

@app.get("/alerts")
def alerts():
    return rows("alerts")

@app.post("/alerts")
def create_alert(payload: Dict[str, Any]):
    channels = payload.get("channels") or {}
    recipients = payload.get("recipients") or []
    values = (datetime.now().isoformat(timespec="seconds"), payload["district"], payload["risk_level"], payload["language"], payload["message"])
    alert_id = insert_alert(values)
    email_result = {"status":"disabled","sent":0,"failed":0,"detail":[]}
    if channels.get("email"):
        email_result = dispatch_email(payload.get("subject", "LandslideGuard NER Alert"), payload["message"], recipients)
    return {"id":alert_id,"status":"recorded","dispatch_status":"queued","email_status":email_result["status"],"email_sent":email_result["sent"],"email_failed":email_result.get("failed",0),"email_detail":email_result.get("detail",[]),"mobile_status":mobile_push_status(bool(channels.get("mobile"))),"channels":channels,"recipients_count":len(recipients),"audit":bool(payload.get("audit",True))}

@app.post("/incidents")
async def create_incident(
    reporter: str = Form("Field Team"),
    district: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    incident_type: str = Form(...),
    severity: str = Form(...),
    description: str = Form(""),
    photo: UploadFile | None = File(None),
):
    photo_path = ""
    quality = 0.0
    triage = "UNASSESSED"

    if photo:
        raw = await photo.read()
        analysis = analyze_image(raw)
        quality = analysis["quality"]
        triage = analysis["triage_label"]
        suffix = Path(photo.filename or "photo.jpg").suffix.lower() or ".jpg"
        photo_path = str(UPLOAD_DIR / f"incident_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{suffix}")
        Path(photo_path).write_bytes(raw)

    incident_id = insert_incident((
        datetime.now().isoformat(timespec="seconds"), reporter, district,
        latitude, longitude, incident_type, severity, description,
        photo_path, quality, triage
    ))
    return {"id":incident_id, "visual_quality":quality, "triage_label":triage}

@app.get("/dashboard")
def dashboard():
    zones_data = []
    for z in all_zones():
        p = predict(z["features"])
        zones_data.append({**{k:v for k,v in z.items() if k!="features"}, **p})
    levels = [z["risk_level"] for z in zones_data]
    return {
        "zones": zones_data,
        "high_or_critical": sum(x in ("HIGH","CRITICAL") for x in levels),
        "critical": levels.count("CRITICAL"),
        "incidents": len(rows("incidents")),
        "alerts": len(rows("alerts")),
    }
