# ⛰️ LandslideGuard NER — SIH 2026 Winner-Grade Prototype

**SIH Problem Statement:** 26001  
**Theme:** Disaster Management  
**Focus:** AI-Based Early Warning and Landslide Risk Monitoring System in North Eastern Region (NER)

> A decision-intelligence platform that moves disaster management from **reactive reporting to predictive, explainable and location-aware action**.

---

## 👥 Core Contributors & Team

Meet the team behind **LandslideGuard NER** built for SIH 2026.

| Contributor | Role & Focus Area | GitHub / Socials |
| :---: | :--- | :---: |
| <img src="https://github.com/sxham69.png" width="80" style="border-radius:50%"><br>**[Member Name]** | **Team Lead & ML Architect**<br>• Designed dynamic risk fusion engine (`risk_engine.py`) & XAI Digital Twin<br>• Engineered uncertainty-aware scoring & incident photo triage (`incident_ai.py`) | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/sxham69) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/) |
| <img src="https://github.com/github.png" width="80" style="border-radius:50%"><br>**[Member Name]** | **Lead Backend & Systems Engineer**<br>• Developed core FastAPI service layer (`backend/api.py`) & SQLite persistence<br>• Built SMTP broadcast integration & offline-first data engines (`data_engine.py`) | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/) |
| <img src="https://github.com/github.png" width="80" style="border-radius:50%"><br>**[Member Name]** | **Backend & Dispatch Engineer**<br>• Built multilingual alert engine (English, Assamese, Bengali, Hindi, Nepali)<br>• Engineered audit log persistence & emergency dispatch API endpoints | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/) |
| <img src="https://github.com/github.png" width="80" style="border-radius:50%"><br>**[Member Name]** | **Lead Frontend & UX Architect**<br>• Designed Streamlit State EOC Command Center UI (`frontend/app.py`)<br>• Built dark-theme NER risk map & explainable AI commander briefing view | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/) |
| <img src="https://github.com/github.png" width="80" style="border-radius:50%"><br>**[Member Name]** | **Frontend & Resilience UI Engineer**<br>• Built demo-resilient analytics surfaces & mobile alert notification preview<br>• Developed field-intelligence reporting forms & live KPI cards dashboard | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/) |
| <img src="https://github.com/github.png" width="80" style="border-radius:50%"><br>**[Member Name]** | **GIS & Geospatial Data Engineer**<br>• Curated North Eastern Region (NER) terrain, slope, and soil-saturation adapters<br>• Integrated road proximity matrix & strategic asset exposure priorities | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/) |

## 1. Why this can stand out

Most disaster dashboards stop at a map and a risk number. LandslideGuard builds a complete operational loop:

**SENSE → FUSE → PREDICT → EXPLAIN → SIMULATE → PRIORITIZE → ALERT → VERIFY → LEARN**

### Core innovations

1. **Multi-signal risk fusion**
   - Rainfall accumulation
   - Soil saturation
   - Slope/terrain
   - Vegetation
   - Historical event density
   - Road proximity
   - Field observations

2. **Dynamic Risk Index**
   - Risk is not just “rainfall > threshold”.
   - The model combines environmental and historical evidence.

3. **Uncertainty-aware AI**
   - Every prediction includes confidence.
   - Low-confidence predictions are routed for human verification.

4. **Digital Twin / What-if simulator**
   - Judges can increase rainfall, saturation and slope conditions.
   - The system instantly estimates how risk changes.

5. **Impact-aware prioritization**
   - Two equally risky slopes do not have equal consequences.
   - The system factors critical roads, villages and infrastructure exposure.

6. **Citizen + field intelligence**
   - Field teams can submit geo-tagged observations and photographs.
   - Reports become future training/validation data.

7. **Multilingual emergency communication**
   - English, Hindi, Assamese, Bengali and Nepali templates.

8. **Human-in-the-loop safety**
   - The AI recommends action.
   - It does not independently order evacuation.

9. **Offline-first production architecture**
   - Designed for intermittent connectivity in remote NER terrain.

10. **Auditability**
    - Alerts and field reports are persisted with timestamps.

---

## 2. Run locally

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
# .venv\Scripts\activate

pip install -r requirements.txt

# Start the API
uvicorn backend.api:app --reload --port 8000

# In another terminal start the dashboard
streamlit run frontend/app.py
```

The dashboard can run in demo mode even if the API is unavailable.

---

## 3. One-command demo

### macOS/Linux
```bash
./run.sh
```

### Windows
```bat
run.bat
```

---

## 4. Recommended SIH demo sequence

### Minute 1 — The problem
Show Command Center:
- NER overview
- high-risk zones
- exposed roads
- active field reports

### Minute 2 — Predictive AI
Open **AI Digital Twin**:
- increase 24h rainfall
- increase soil saturation
- increase slope
- watch risk score and confidence change

### Minute 3 — Explainability
Show:
- risk contributors
- feature importance
- recommended response

### Minute 4 — Impact
Change the affected asset:
- normal road → strategic highway
- low population → high population

Show that **operational priority changes even when hazard risk is similar**.

### Minute 5 — Field intelligence
Submit a photo/incident:
- slope crack
- rockfall
- road blockage

It appears on the map.

### Minute 6 — Alert
Generate a multilingual warning and show the audit trail.

### Minute 7 — Close
Explain that the prototype is the operational layer connecting:
**weather + sensors + satellite + GIS + AI + field teams + citizens + alerts**.

---

## 5. Production data integrations

The current project deliberately uses deterministic demo data so it can run on a judging laptop.

Replace the adapters in `backend/data_engine.py` with approved production sources:

- IMD rainfall/weather feeds
- IoT soil-moisture sensors
- DEM / slope / aspect layers
- Sentinel-1 deformation products
- Sentinel-2 vegetation / land-cover products
- road and infrastructure GIS
- historical landslide inventory
- government field reports

Do not connect an unvalidated model directly to emergency operations.

---

## 6. Project structure

```text
LandslideGuard_NER_SIH_Winner/
├── backend/
│   ├── api.py                 # FastAPI service
│   ├── database.py            # SQLite persistence
│   ├── data_engine.py         # Demo sensor + GIS data adapters
│   ├── risk_engine.py         # AI inference + uncertainty + explanation
│   └── incident_ai.py         # photo quality / visual triage
├── frontend/
│   └── app.py                 # SIH command center
├── ml/
│   └── train.py               # reproducible training pipeline
├── data/
│   ├── sample_sensor_data.csv
│   └── uploads/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SIH_PITCH.md
│   ├── DEMO_SCRIPT.md
│   ├── NOVELTY.md
│   └── PRODUCTION_ROADMAP.md
├── tests/
│   └── test_core.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.sh
└── run.bat
```

---

## 7. Safety statement

This is a hackathon prototype and not an emergency-certified warning system. Operational thresholds, model validation, alert escalation and evacuation decisions must be approved by relevant disaster-management, geotechnical and government authorities.


## 8. Command-center broadcast layer

The upgraded dashboard adds a realistic State EOC presentation with animated system health, live alert ticker, KPI cards, explainable AI commander briefing, NER dark-theme risk map, mobile notification preview, and an authorized alert dispatch workflow.

Email delivery is integrated through a standard SMTP adapter. Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and `EMAIL_FROM` in `.env`. Gmail users should use a Google App Password. If SMTP is not configured, the demo safely records the intended email delivery without sending anything. Replace the adapter with the approved government email gateway for production.


## 9. Demo-resilient analytics and mobile alert surfaces

The frontend is intentionally resilient for SIH judging/demo environments:
- **Resilience Analytics** automatically switches to deterministic NER demo data if the API is unavailable.
- **Mobile Alert Preview** automatically shows clearly labeled, realistic demo emergency notifications when no live alert has been created.
- Live API data takes precedence whenever the backend is available.
- Demo notifications are display-only and are never sent to real recipients.

## 10. macOS setup / `pip: command not found` fix

Use the included launcher instead of calling a global `pip` or `streamlit` command:

```bash
./run.sh
```

For a clean environment:

```bash
./setup_mac.sh
./run.sh
```

The launcher always uses `.venv/bin/python -m pip` and `.venv/bin/python -m streamlit`, so it does not depend on shell PATH entries. It also bootstraps pip when the virtual environment was created without it. Python 3.11/3.12 is preferred for compatibility with the ML dependencies.


## Mac quick start

If macOS reports `zsh: permission denied: ./run.sh`, run:

```bash
chmod +x run.sh setup_mac.sh
./setup_mac.sh
./run.sh
```

The included `run_mac.command` can also be double-clicked from Finder after extraction. The launcher uses `.venv/bin/python -m ...`, so it does not depend on global `pip` or `streamlit` PATH commands.



## Live email setup

The Alert Center uses **email instead of phone/SMS** for alert delivery. No phone number or Twilio sender is required.

### Gmail
1. Enable 2-Step Verification on the sending Google account.
2. Create a Google **App Password**.
3. Copy `.env.example` to `.env`.
4. Set `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USERNAME` to your Gmail address, `SMTP_PASSWORD` to the App Password, and `EMAIL_FROM` to the same address.
5. Start the project with `./run.sh`.
6. In **Alert Center**, enter one or more email recipients and click **AUTHORIZE & DISPATCH ALERT**.

The **SEND TEST EMAIL** button is also available in Alert Center. Outlook/Microsoft 365 and other SMTP providers can be used by changing the SMTP host and credentials. Mobile notification remains a display-only simulation in this prototype.
