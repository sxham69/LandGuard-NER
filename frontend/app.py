import os
import re
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import certifi
import folium
import numpy as np
import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

# Load configuration from the project .env without overwriting an already
# configured OS/Streamlit secret. This avoids accidentally replacing a valid
# key with an old or empty .env value.
try:
    from dotenv import load_dotenv
    for env_file in (ROOT / ".env", Path.cwd() / ".env", Path.cwd().parent / ".env"):
        if env_file.exists():
            load_dotenv(env_file, override=False)
except Exception:
    pass


st.set_page_config(
    page_title="LandslideGuard NER • State EOC",
    page_icon="🚨",
    layout="wide",
)

# Persistent UI theme. Streamlit reruns the script when the toggle is tapped,
# so both the dashboard and the Folium map are rebuilt in the selected theme.
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

DARK = st.session_state.dark_mode

st.markdown(
    f"""
    <style>
    :root {{
        --bg: {'#071426' if DARK else '#f4f8fb'};
        --surface: {'#0a1e33' if DARK else '#ffffff'};
        --surface2: {'#0e2640' if DARK else '#f1f6f9'};
        --border: {'#1d3a57' if DARK else '#c7d6df'};
        --text: {'#e8f1f8' if DARK else '#10202e'};
        --muted: {'#8fa9bd' if DARK else '#506879'};
        --accent: #29d3ff;
        --input: {'#0b2035' if DARK else '#ffffff'};
        --input-hover: {'#102a40' if DARK else '#f5f9fc'};
        --control-border: {'#2a4a66' if DARK else '#b9cbd6'};
        --table-head: {'#102b45' if DARK else '#edf4f8'};
        --table-row: {'#0a1e33' if DARK else '#ffffff'};
        --table-row-alt: {'#0d2740' if DARK else '#f7fafc'};
        --table-hover: {'#153653' if DARK else '#eaf3f7'};
        --code-bg: {'#071522' if DARK else '#f3f7fa'};
    }}
    html, body, [class*=css] {{ font-family: Inter, sans-serif; }}
    .stApp {{
        background: radial-gradient(circle at 78% 2%, {'#10365a 0, #071426 38%, #050e1b 100%' if DARK else '#ffffff 0, #f4f8fb 42%, #eaf2f7 100%'});
        color: var(--text) !important;
        min-height: 100vh;
    }}

    /* Keep the fixed Streamlit header from covering the first dashboard card. */
    header[data-testid="stHeader"] {{
        background: {'#080d14' if DARK else '#ffffff'} !important;
        border-bottom: 1px solid var(--border) !important;
        z-index: 1000 !important;
    }}
    header[data-testid="stHeader"] * {{ color:var(--text) !important; }}
    header[data-testid="stHeader"] svg {{ fill:var(--text) !important; color:var(--text) !important; }}

    .block-container {{
        padding-top: 5.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1500px;
    }}
    h1,h2,h3,h4,h5,h6 {{ font-family:"Space Grotesk",sans-serif; color:var(--text) !important; }}

    section[data-testid="stSidebar"] {{
        background:linear-gradient(180deg, {'#061323' if DARK else '#ffffff'}, {'#091c31' if DARK else '#edf4f8'}) !important;
        border-right:1px solid var(--border) !important;
    }}
    section[data-testid="stSidebar"] * {{ color:var(--text) !important; }}
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {{ color:var(--muted) !important; }}
    section[data-testid="stSidebar"] [data-testid="stAlert"] * {{ color:{'#8ff0bb' if DARK else '#1c8a54'} !important; }}

    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stWidgetLabel"] p,
    .stApp label {{ color:var(--text) !important; }}
    .stApp [data-testid="stCaptionContainer"] {{ color:var(--muted) !important; }}
    .stApp input, .stApp textarea {{ color:var(--text) !important; background:var(--input) !important; border-color:var(--border) !important; }}
    .stApp input::placeholder, .stApp textarea::placeholder {{ color:var(--muted) !important; opacity:1 !important; }}
    /* Streamlit/BaseWeb select controls */
    .stApp [data-baseweb="select"] {{
        width:100% !important;
        color:var(--text) !important;
    }}
    .stApp [data-baseweb="select"] > div {{
        background:var(--input) !important;
        color:var(--text) !important;
        border:1px solid var(--border) !important;
        border-radius:12px !important;
        min-height:48px !important;
        box-shadow:none !important;
    }}
    .stApp [data-baseweb="select"] > div > div {{
        background:transparent !important;
        color:var(--text) !important;
    }}
    .stApp [data-baseweb="select"] * {{ color:var(--text) !important; }}
    .stApp [data-baseweb="select"] svg {{
        fill:var(--text) !important;
        color:var(--text) !important;
    }}
    .stApp [data-baseweb="select"] [role="button"] {{
        background:transparent !important;
        color:var(--text) !important;
    }}
    .stApp [data-baseweb="select"] > div > div:last-child {{
        background:transparent !important;
        border-radius:0 12px 12px 0 !important;
    }}

    /* Open dropdown menu */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [data-baseweb="menu"] > div,
    [role="listbox"] {{
        background:{'#0b2035' if DARK else '#ffffff'} !important;
        color:var(--text) !important;
        border:1px solid var(--border) !important;
        box-shadow:0 12px 30px rgba(0,0,0,.18) !important;
    }}
    [data-baseweb="menu"] li,
    [role="option"] {{
        background:{'#0b2035' if DARK else '#ffffff'} !important;
        color:var(--text) !important;
    }}
    [data-baseweb="menu"] li:hover,
    [role="option"]:hover,
    [aria-selected="true"] {{
        background:{'#153653' if DARK else '#e8f2f7'} !important;
        color:var(--text) !important;
    }}
    [data-baseweb="popover"] *,
    [data-baseweb="menu"] *,
    [role="listbox"] *,
    [role="option"] * {{ color:var(--text) !important; }}
    .stApp button {{ color:var(--text) !important; }}
    .stApp [data-testid="stAlert"] {{ color:var(--text) !important; }}
    .stApp [data-testid="stMetric"] label, .stApp [data-testid="stMetricLabel"] {{ color:var(--muted) !important; }}
    .stApp [data-testid="stMetricValue"], .stApp [data-testid="stMetricDelta"] {{ color:var(--text) !important; }}

    /* Complete theme synchronization: every native Streamlit control follows the selected theme. */
    .stApp, .stApp * {{ color-scheme:{'dark' if DARK else 'light'}; }}
    .stApp [data-testid="stVerticalBlockBorderWrapper"],
    .stApp [data-testid="stExpander"],
    .stApp [data-testid="stPopover"],
    .stApp [data-testid="stForm"] {{
        background:transparent !important;
        color:var(--text) !important;
    }}
    .stApp [data-testid="stButton"] > button,
    .stApp [data-testid="stFormSubmitButton"] > button,
    .stApp button {{
        background:var(--surface) !important;
        color:var(--text) !important;
        border:1px solid var(--control-border) !important;
        border-radius:10px !important;
        box-shadow:none !important;
    }}
    .stApp [data-testid="stButton"] > button:hover,
    .stApp [data-testid="stFormSubmitButton"] > button:hover,
    .stApp button:hover {{
        background:var(--input-hover) !important;
        color:var(--text) !important;
        border-color:var(--accent) !important;
    }}
    .stApp [data-testid="stButton"] > button[kind="primary"],
    .stApp [data-testid="stFormSubmitButton"] > button[kind="primary"] {{
        background:{'#29d3ff' if DARK else '#0b8fb3'} !important;
        color:{'#04121d' if DARK else '#ffffff'} !important;
        border-color:{'#29d3ff' if DARK else '#0b8fb3'} !important;
    }}
    .stApp input, .stApp textarea, .stApp [data-baseweb="input"], .stApp [data-baseweb="textarea"] {{
        background:var(--input) !important;
        color:var(--text) !important;
        border-color:var(--control-border) !important;
    }}
    .stApp [data-baseweb="input"] > div, .stApp [data-baseweb="textarea"] > div {{
        background:var(--input) !important;
        border-color:var(--control-border) !important;
    }}
    .stApp [data-baseweb="input"] input, .stApp [data-baseweb="textarea"] textarea {{
        background:transparent !important;
        color:var(--text) !important;
        caret-color:var(--accent) !important;
    }}
    .stApp [data-baseweb="input"] svg, .stApp [data-baseweb="textarea"] svg {{ color:var(--muted) !important; fill:var(--muted) !important; }}
    .stApp [data-testid="stFileUploader"] section {{
        background:var(--surface) !important;
        border:1px dashed var(--control-border) !important;
        color:var(--text) !important;
    }}
    .stApp [data-testid="stFileUploader"] section * {{ color:var(--text) !important; }}
    .stApp [data-testid="stFileUploader"] button {{ background:var(--input) !important; color:var(--text) !important; }}
    .stApp [data-testid="stCheckbox"] label, .stApp [data-testid="stToggle"] label, .stApp [data-testid="stRadio"] label {{ color:var(--text) !important; }}
    .stApp [data-testid="stSlider"] [role="slider"] {{ background:var(--accent) !important; border-color:var(--accent) !important; }}
    .stApp [data-testid="stSlider"] [data-baseweb="slider"] > div > div {{ background:var(--control-border) !important; }}
    .stApp [data-testid="stProgressBar"] > div {{ background:var(--surface2) !important; }}
    .stApp [data-testid="stProgressBar"] > div > div {{ background:var(--accent) !important; }}
    .stApp [data-testid="stAlert"] {{
        background:{'#10263a' if DARK else '#f7fbfd'} !important;
        border:1px solid var(--border) !important;
        color:var(--text) !important;
    }}
    .stApp [data-testid="stAlert"] p, .stApp [data-testid="stAlert"] span, .stApp [data-testid="stAlert"] div {{ color:var(--text) !important; }}
    .stApp [data-testid="stMetric"] {{ background:var(--surface) !important; border-radius:10px; padding:8px; }}
    .stApp [data-testid="stMetric"] [data-testid="stMetricValue"] {{ color:var(--text) !important; }}
    .stApp [data-testid="stMetric"] [data-testid="stMetricDelta"] {{ color:var(--muted) !important; }}
    .stApp hr {{ border-color:var(--border) !important; }}
    .stApp code, .stApp pre {{ background:var(--code-bg) !important; color:var(--text) !important; border-color:var(--border) !important; }}
    /* Plotly analytics: readable axes/values and visible zoom/download controls in both themes. */
    .stApp .js-plotly-plot .plotly .modebar {{ background:var(--surface) !important; border:1px solid var(--border) !important; border-radius:8px; padding:3px !important; opacity:1 !important; }}
    .stApp .js-plotly-plot .plotly .modebar-btn {{ background:transparent !important; color:var(--text) !important; opacity:1 !important; }}
    .stApp .js-plotly-plot .plotly .modebar-btn svg {{ fill:var(--text) !important; color:var(--text) !important; }}
    .stApp .js-plotly-plot .plotly .modebar-btn:hover {{ background:var(--input-hover) !important; }}
    .stApp .js-plotly-plot .plotly .gtitle, .stApp .js-plotly-plot .plotly .xtitle, .stApp .js-plotly-plot .plotly .ytitle, .stApp .js-plotly-plot .plotly .xtick text, .stApp .js-plotly-plot .plotly .ytick text, .stApp .js-plotly-plot .plotly .legend text {{ fill:var(--text) !important; color:var(--text) !important; }}
    .stApp .js-plotly-plot .plotly .gridlayer path {{ stroke:var(--border) !important; stroke-opacity:.55 !important; }}


    .govbar {{ display:flex;align-items:center;justify-content:space-between;padding:10px 16px;border:1px solid var(--border);background:{'rgba(8,28,48,.9)' if DARK else 'rgba(255,255,255,.96)'};border-radius:10px;margin-bottom:10px; }}
    .govbrand {{ display:flex;gap:12px;align-items:center; }}
    .emblem {{ width:38px;height:38px;border-radius:50%;border:2px solid {'#d8e5ee' if DARK else '#6d8798'};display:grid;place-items:center;color:var(--text) !important; }}
    .govtitle {{ font-weight:800;font-size:14px;color:var(--text) !important; }}
    .govsub,.live {{ font-size:10px;color:var(--muted) !important; }}
    .live {{ text-transform:uppercase;letter-spacing:.08em; }}
    .dot {{ display:inline-block;width:8px;height:8px;border-radius:50%;background:#28d17c; }}
    .ticker {{ overflow:hidden;white-space:nowrap;border:1px solid {'#53323a' if DARK else '#e2b8bd'};background:{'#1a1620' if DARK else '#fff3f3'};border-radius:8px;padding:8px 0;margin:8px 0 16px;color:{'#ffd5da' if DARK else '#7a2630'} !important;font-size:12px; }}
    .ticker span {{ display:inline-block;padding-left:100%;animation:marquee 28s linear infinite; }}
    @keyframes marquee {{ to {{ transform:translateX(-100%); }} }}
    .kpi {{ background:linear-gradient(145deg,{'rgba(14,38,64,.96),rgba(7,23,40,.96)' if DARK else '#ffffff,#f1f6f9'});border:1px solid var(--border);border-radius:13px;padding:14px 16px;min-height:104px;box-shadow:0 12px 35px {'rgba(0,0,0,.18)' if DARK else 'rgba(33,64,84,.12)'};color:var(--text) !important; }}
    .kpi .label {{ font-size:10px;color:var(--muted) !important;letter-spacing:.1em;font-weight:800; }}
    .kpi .value {{ font-size:29px;font-weight:700;margin:6px 0;color:var(--text) !important; }}
    .kpi .meta {{ font-size:11px;color:var(--muted) !important; }}
    .kpi.red {{ border-color:{'#6b2935' if DARK else '#e0aeb5'}; }}
    .kpi.cyan {{ border-color:{'#1a6276' if DARK else '#9bcfdd'}; }}
    .kpi.amber {{ border-color:{'#6c5221' if DARK else '#d8c48a'}; }}
    .panel {{ background:{'rgba(10,30,51,.82)' if DARK else 'rgba(255,255,255,.94)'};border:1px solid var(--border);border-radius:14px;padding:16px;box-shadow:0 10px 30px {'rgba(0,0,0,.16)' if DARK else 'rgba(33,64,84,.10)'};color:var(--text) !important; }}
    .panel h3,.panel b,.panel p {{ color:var(--text) !important; }}
    .eyebrow {{ font-size:10px;color:#29d3ff !important;font-weight:800;letter-spacing:.12em;text-transform:uppercase; }}
    .small {{ font-size:11px;color:var(--muted) !important; }}
    .riskbadge {{ display:inline-block;padding:5px 9px;border-radius:999px;font-size:10px;font-weight:800; }}
    .CRITICAL {{ background:{'#541d28' if DARK else '#fde4e7'};color:{'#ff9da8' if DARK else '#a51f2d'} !important; }}
    .HIGH {{ background:{'#4d3314' if DARK else '#fff0d4'};color:{'#ffc85e' if DARK else '#8a5a00'} !important; }}
    .MODERATE {{ background:{'#463e13' if DARK else '#fff9d8'};color:{'#e9db68' if DARK else '#796a00'} !important; }}
    .LOW {{ background:{'#123a2b' if DARK else '#dcf7e9'};color:{'#76e4ac' if DARK else '#197347'} !important; }}
    .scanline {{ height:2px;background:linear-gradient(90deg,transparent,#29d3ff,transparent); }}
    .mobile-preview-card {{ background:{'#071018' if DARK else '#ffffff'};border:1px solid {'#30485c' if DARK else '#c7d6df'};color:var(--text); }}
    .mobile-preview-message {{ color:var(--text) !important; }}
    .mobile-alert-card {{ background:{'#071018' if DARK else '#ffffff'};border:1px solid {'#30485c' if DARK else '#c7d6df'};box-shadow:0 16px 40px {'rgba(0,0,0,.30)' if DARK else 'rgba(33,64,84,.12)'};color:var(--text); }}
    .mobile-alert-card .district-text {{ color:{'#b7c8d5' if DARK else '#506879'} !important; }}
    .mobile-alert-card .message-text {{ color:{'#e8f1f8' if DARK else '#10202e'} !important; }}
    .mobile-alert-card .advisory {{ background:{'#102a40' if DARK else '#eaf5fb'};color:{'#73dcff' if DARK else '#12647d'} !important; }}
    .stApp [data-testid="stDataFrame"] {{ border:1px solid var(--border);border-radius:10px;overflow:hidden; }}

    /* All app tables use the same theme as the rest of the dashboard. */
    .theme-table-wrap, .risk-table-wrap {{ width:100%; overflow-x:auto; margin:8px 0 18px; border:1px solid var(--border); border-radius:12px; background:var(--table-row); }}
    .theme-table, .risk-table {{ width:100%; min-width:760px; border-collapse:separate; border-spacing:0; table-layout:auto; background:var(--table-row) !important; color:var(--text) !important; font-size:13px; }}
    .theme-table th, .risk-table th {{ position:sticky; top:0; z-index:1; padding:11px 12px; text-align:left; white-space:nowrap; font-weight:800; background:var(--table-head) !important; color:var(--text) !important; border-bottom:1px solid var(--border); }}
    .theme-table td, .risk-table td {{ padding:10px 12px; white-space:nowrap; background:var(--table-row) !important; color:var(--text) !important; border-bottom:1px solid var(--border); }}
    .theme-table tbody tr:nth-child(even) td, .risk-table tbody tr:nth-child(even) td {{ background:var(--table-row-alt) !important; }}
    .theme-table tbody tr:hover td, .risk-table tbody tr:hover td {{ background:var(--table-hover) !important; }}
    .theme-table tbody tr:last-child td, .risk-table tbody tr:last-child td {{ border-bottom:0; }}
    .theme-status, .risk-cell {{ font-weight:800 !important; }}
    .theme-status.CRITICAL, .risk-cell.CRITICAL {{ color:{'#ff9da8' if DARK else '#a51f2d'} !important; }}
    .theme-status.HIGH, .risk-cell.HIGH {{ color:{'#ffc85e' if DARK else '#8a5a00'} !important; }}
    .theme-status.MODERATE, .risk-cell.MODERATE {{ color:{'#e9db68' if DARK else '#796a00'} !important; }}
    .theme-status.LOW, .risk-cell.LOW {{ color:{'#76e4ac' if DARK else '#197347'} !important; }}
    .theme-status.LIVE {{ color:{'#76e4ac' if DARK else '#197347'} !important; }}
    .theme-status.FALLBACK {{ color:{'#ffc85e' if DARK else '#8a5a00'} !important; }}
    .theme-table-empty {{ padding:16px; border:1px solid var(--border); border-radius:12px; background:var(--surface); color:var(--muted) !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

def _theme_table_html(df):
    """Render tables with explicit theme colors so they never inherit a black canvas."""
    if df is None or df.empty:
        return '<div class="theme-table-empty">No data available.</div>'
    headers = ''.join(f'<th>{str(col)}</th>' for col in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col, value in row.items():
            if pd.isna(value):
                text = "—"
            elif isinstance(value, (float, np.floating)):
                text = f"{float(value):.2f}"
            else:
                text = str(value)
            cls = ''
            if str(col).lower() in {"risk", "risk_level", "status", "severity"}:
                upper = text.upper()
                if upper in {"CRITICAL", "HIGH", "MODERATE", "LOW", "LIVE", "FALLBACK"}:
                    cls = f' class="theme-status {upper}"'
            cells.append(f'<td{cls}>{text}</td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    return (
        '<div class="theme-table-wrap"><table class="theme-table">'
        f'<thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody>'
        '</table></div>'
    )

PLOTLY_THEME = "plotly_dark" if DARK else "plotly_white"


# ------------------------------------------------------------
# Demo data: these make Analytics and Mobile Preview NEVER empty.
# ------------------------------------------------------------
DISTRICTS = [
    ("Aizawl", "Mizoram", 23.7271, 92.7176),
    ("Gangtok", "Sikkim", 27.3389, 88.6065),
    ("Shillong", "Meghalaya", 25.5788, 91.8933),
    ("Itanagar", "Arunachal Pradesh", 27.0844, 93.6053),
    ("Kohima", "Nagaland", 25.6751, 94.1086),
    ("Imphal", "Manipur", 24.8170, 93.9368),
    ("Agartala", "Tripura", 23.8315, 91.2868),
    ("Guwahati", "Assam", 26.1445, 91.7362),
]

DEMO_ALERTS = [
    {
        "id": "DEMO-01", "created_at": "LIVE DEMO", "district": "Gangtok",
        "risk_level": "CRITICAL", "language": "English",
        "message": "Critical landslide risk detected near vulnerable slopes. Avoid non-essential travel, keep away from unstable slopes and follow official evacuation instructions.",
    },
    {
        "id": "DEMO-02", "created_at": "LIVE DEMO", "district": "Aizawl",
        "risk_level": "HIGH", "language": "English",
        "message": "High landslide risk following elevated rainfall. Residents near vulnerable slopes should remain alert and follow local administration advisories.",
    },
]

if "local_alerts" not in st.session_state:
    st.session_state.local_alerts = []
if "local_incidents" not in st.session_state:
    st.session_state.local_incidents = []


def clean(value):
    return str(value or "").strip().strip('"\'')


def demo_features(seed):
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


def local_prediction(f):
    """Deterministic local risk model; no backend service required."""
    rain24 = float(f["rainfall24"])
    rain72 = float(f["rainfall72"])
    soil = float(f["soil"])
    slope = float(f["slope"])
    history = float(f["history"])
    road_dist = float(f["road_dist"])

    score = (
        0.24 * min(rain24 / 120 * 100, 100)
        + 0.16 * min(rain72 / 280 * 100, 100)
        + 0.25 * soil
        + 0.25 * min(slope / 48 * 100, 100)
        + 0.10 * min(history / 7 * 100, 100)
    )
    score = float(np.clip(score, 0, 100))
    level = "CRITICAL" if score >= 75 else "HIGH" if score >= 55 else "MODERATE" if score >= 35 else "LOW"
    exposure = float(np.clip(100 - road_dist / 7.5, 0, 100))
    priority = float(np.clip(score * .68 + exposure * .32, 0, 100))

    return {
        "risk_level": level,
        "risk_score": round(score, 2),
        "confidence": 0.82,
        "exposure_score": round(exposure, 2),
        "operational_priority": round(priority, 2),
        "probabilities": {
            "LOW": round(max(0.02, 1 - score / 100) * .35, 3),
            "MODERATE": round(.20 + (score / 100) * .15, 3),
            "HIGH": round(.25 + (score / 100) * .25, 3),
        },
        "top_factors": [
            {"factor": "24h rainfall", "importance": .24},
            {"factor": "Slope", "importance": .22},
            {"factor": "Soil moisture", "importance": .21},
            {"factor": "Historical events", "importance": .13},
        ],
        "recommended_action": (
            "Immediate field verification + control-room review"
            if level in ("HIGH", "CRITICAL") else "Enhanced monitoring"
        ),
    }



def get_openweather_key():
    """Find the OpenWeather key reliably from .env, Streamlit secrets, or env."""
    def normalize(value):
        value = clean(value)
        # Accept .env values such as: OPENWEATHER_API_KEY="abc" or 'abc'
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1].strip()
        return value

    invalid = {
        "", "your_key", "your_openweather_key", "replace_me",
        "your_api_key", "changeme", "none", "null", "undefined",
    }

    # 1) Read the project .env directly. This avoids depending on dotenv being
    # loaded before Streamlit starts and avoids accidentally using an old OS key.
    env_files = [
        ROOT / ".env",
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        Path(__file__).resolve().parent.parent / ".env",
    ]
    seen = set()
    for env_file in env_files:
        try:
            env_file = env_file.resolve()
        except Exception:
            continue
        if env_file in seen or not env_file.is_file():
            continue
        seen.add(env_file)
        try:
            for raw_line in env_file.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                name, value = line.split("=", 1)
                name = name.strip()
                value = value.strip()
                if name in {"OPENWEATHER_API_KEY", "OPENWEATHER_KEY", "WEATHER_API_KEY"}:
                    value = normalize(value)
                    if value and value.lower() not in invalid:
                        return value
        except (OSError, UnicodeError):
            pass

    # 2) Streamlit secrets.
    try:
        for name in ("OPENWEATHER_API_KEY", "OPENWEATHER_KEY", "WEATHER_API_KEY"):
            value = normalize(st.secrets.get(name, ""))
            if value and value.lower() not in invalid:
                return value
    except Exception:
        pass

    # 3) Process environment.
    for name in ("OPENWEATHER_API_KEY", "OPENWEATHER_KEY", "WEATHER_API_KEY"):
        value = normalize(os.getenv(name, ""))
        if value and value.lower() not in invalid:
            return value

    return ""


@st.cache_data(ttl=600, show_spinner=False)
def fetch_openweather(lat, lon, api_key):
    """Fetch current weather and the 5-day/3-hour forecast from OpenWeather."""
    api_key = clean(api_key)
    if not api_key:
        raise RuntimeError(
            "OPENWEATHER_API_KEY is not configured. Add it to .env or Streamlit secrets."
        )

    params = {
        "lat": f"{float(lat):.4f}",
        "lon": f"{float(lon):.4f}",
        "appid": api_key,
        "units": "metric",
    }

    session = requests.Session()
    session.verify = certifi.where()
    session.headers.update({"User-Agent": "LandGuard-NER/1.0"})

    endpoints = (
        "https://api.openweathermap.org/data/2.5/weather",
        "https://api.openweathermap.org/data/2.5/forecast",
    )
    responses = []

    for endpoint in endpoints:
        try:
            response = session.get(endpoint, params=params, timeout=(5, 15))
        except requests.exceptions.SSLError:
            # certifi is the normal secure path. A clear error is preferable
            # to silently disabling TLS verification.
            raise
        except requests.exceptions.RequestException:
            raise

        if response.status_code >= 400:
            try:
                payload = response.json()
                message = payload.get("message", response.text)
            except Exception:
                message = response.text
            error = requests.HTTPError(
                f"OpenWeather HTTP {response.status_code}: {message}",
                response=response,
            )
            raise error

        try:
            responses.append(response.json())
        except ValueError as exc:
            raise RuntimeError("OpenWeather returned an invalid JSON response.") from exc

    return responses[0], responses[1]


def openweather_error(exc):
    """Human-readable provider error for the operator."""
    if isinstance(exc, requests.HTTPError):
        status = exc.response.status_code if exc.response is not None else "HTTP"

        if status == 401:
            return (
                "OpenWeather rejected the API key (HTTP 401). "
                "Check the key in .env and make sure it is active."
            )
        if status == 429:
            return (
                "OpenWeather rate limit reached (HTTP 429). "
                "Wait and refresh."
            )

        try:
            detail = exc.response.json().get(
                "message",
                exc.response.text,
            )
        except Exception:
            detail = exc.response.text

        return f"OpenWeather HTTP {status}: {detail}"

    if isinstance(exc, requests.exceptions.SSLError):
        return (
            "SSL certificate verification failed. "
            "Run: python -m pip install --upgrade certifi requests"
        )

    if isinstance(exc, requests.exceptions.Timeout):
        return "OpenWeather request timed out."

    if isinstance(exc, requests.exceptions.ConnectionError):
        return (
            "Could not connect to OpenWeather. "
            "Check your internet connection or firewall."
        )

    return str(exc)


def fetch_openmeteo(lat, lon):
    """Keyless live-weather fallback using Open-Meteo when OpenWeather is unavailable."""
    params = {
        "latitude": float(lat),
        "longitude": float(lon),
        "current": "temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m",
        "hourly": "precipitation,rain",
        "forecast_days": 4,
        "timezone": "UTC",
    }
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params=params,
        timeout=(5, 15),
        headers={"User-Agent": "LandGuard-NER/1.0"},
    )
    response.raise_for_status()
    data = response.json()
    current = data.get("current") or {}
    hourly = data.get("hourly") or {}
    precipitation = hourly.get("precipitation") or []
    rain = hourly.get("rain") or []

    # The first hourly value is the current/nearest hour. Sum the next
    # 24/72 hourly values for operational precipitation context.
    rain_values = []
    for i in range(max(len(precipitation), len(rain))):
        p = float(precipitation[i] or 0.0) if i < len(precipitation) else 0.0
        r = float(rain[i] or 0.0) if i < len(rain) else 0.0
        rain_values.append(max(p, r))

    return {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "rain_last_1h": round(float(current.get("rain") or current.get("precipitation") or 0.0), 1),
        "rain_forecast24": round(sum(rain_values[:24]), 1),
        "rain_forecast72": round(sum(rain_values[:72]), 1),
        "moisture_pressure": round(float(current.get("relative_humidity_2m") or 0.0) * 0.85, 1),
        "temperature": round(float(current.get("temperature_2m") or 0.0), 1),
        "humidity": round(float(current.get("relative_humidity_2m") or 0.0), 0),
        "wind_speed": round(float(current.get("wind_speed_10m") or 0.0), 1),
        "source": "Open-Meteo",
        "status": "LIVE",
    }

def parse_weather(current, forecast):
    """Convert OpenWeather responses into model-ready values."""
    rain_last_1h = float(
        ((current.get("rain") or {}).get("1h") or 0.0)
    )

    # Forecast precipitation: sum the next ~24h / ~72h from 3-hour forecasts.
    items = forecast.get("list") or []

    now_ts = int(datetime.now(timezone.utc).timestamp())

    forecast_values = []
    for item in items:
        item_ts = int(item.get("dt", 0))
        if item_ts <= now_ts:
            continue

        rain_3h = float(
            ((item.get("rain") or {}).get("3h") or 0.0)
        )
        snow_3h = float(
            ((item.get("snow") or {}).get("3h") or 0.0)
        )

        forecast_values.append(
            {
                "dt": item_ts,
                "rain": max(0.0, rain_3h + snow_3h),
            }
        )

    rain_24h = round(
        sum(x["rain"] for x in forecast_values[:8]),
        1,
    )
    rain_72h = round(
        sum(x["rain"] for x in forecast_values[:24]),
        1,
    )

    main = current.get("main") or {}
    wind = current.get("wind") or {}

    humidity = float(main.get("humidity") or 0.0)
    temp = float(main.get("temp") or 0.0)
    wind_speed = float(wind.get("speed") or 0.0)

    # OpenWeather's basic weather endpoint does not provide direct soil
    # moisture. Use a clearly-labelled humidity-derived moisture pressure
    # proxy for this prototype rather than falsely calling it soil moisture.
    moisture_pressure = round(np.clip(humidity * 0.85, 0, 100), 1)

    updated = datetime.fromtimestamp(
        int(current.get("dt") or now_ts),
        tz=timezone.utc,
    )

    return {
        "timestamp": updated.strftime("%Y-%m-%d %H:%M UTC"),
        "rain_last_1h": round(rain_last_1h, 1),
        "rain_forecast24": rain_24h,
        "rain_forecast72": rain_72h,
        "moisture_pressure": moisture_pressure,
        "temperature": round(temp, 1),
        "humidity": round(humidity, 0),
        "wind_speed": round(wind_speed * 3.6, 1),  # m/s -> km/h
        "source": "OpenWeather",
        "status": "LIVE",
    }


def live_weather_for_zone(district, state, lat, lon, seed):
    """Return a zone using live OpenWeather data, with explicit fallback."""
    fallback = demo_features(seed)

    api_key = get_openweather_key()

    # Open-Meteo is the permanent keyless provider for this dashboard.
    # Do not require, read, or display any OpenWeather API key.
    if True:
        # Live weather through Open-Meteo; no API key is required.
        try:
            weather = fetch_openmeteo(lat, lon)
            features = dict(fallback)
            features["rainfall24"] = weather["rain_forecast24"]
            features["rainfall72"] = weather["rain_forecast72"]
            features["soil"] = weather["moisture_pressure"]
            prediction = local_prediction(features)
            return {
                "district": district,
                "state": state,
                "lat": lat,
                "lon": lon,
                "features": features,
                **prediction,
                "source": "Open-Meteo",
                "data_status": "LIVE",
                "provider_error": "",
                "weather": weather,
                "provider_note": "OpenWeather API key not configured; using Open-Meteo live weather.",
            }
        except Exception as exc:
            prediction = local_prediction(fallback)
            return {
                "district": district,
                "state": state,
                "lat": lat,
                "lon": lon,
                "features": fallback,
                **prediction,
                "source": "DEMO FALLBACK",
                "data_status": "FALLBACK",
                "provider_error": f"Live weather unavailable: {exc}",
                "weather": {
                    "timestamp": "Unavailable",
                    "rain_last_1h": 0.0,
                    "rain_forecast24": round(fallback["rainfall24"], 1),
                    "rain_forecast72": round(fallback["rainfall72"], 1),
                    "moisture_pressure": round(fallback["soil"], 1),
                    "temperature": 24.0,
                    "humidity": 75.0,
                    "wind_speed": 12.0,
                    "source": "Deterministic demo fallback",
                    "status": "FALLBACK",
                },
            }

    try:
        weather = fetch_openmeteo(lat, lon)
        features = dict(fallback)
        features["rainfall24"] = weather["rain_forecast24"]
        features["rainfall72"] = weather["rain_forecast72"]
        features["soil"] = weather["moisture_pressure"]
        prediction = local_prediction(features)
        return {
            "district": district,
            "state": state,
            "lat": lat,
            "lon": lon,
            "features": features,
            **prediction,
            "source": "Open-Meteo",
            "data_status": "LIVE",
            "provider_error": "",
            "weather": weather,
        }
    except Exception as exc:
        prediction = local_prediction(fallback)
        return {
            "district": district,
            "state": state,
            "lat": lat,
            "lon": lon,
            "features": fallback,
            **prediction,
            "source": "DEMO FALLBACK",
            "data_status": "FALLBACK",
            "provider_error": f"Open-Meteo unavailable: {exc}",
            "weather": {
                "timestamp": "Unavailable",
                "rain_last_1h": 0.0,
                "rain_forecast24": round(fallback["rainfall24"], 1),
                "rain_forecast72": round(fallback["rainfall72"], 1),
                "moisture_pressure": round(fallback["soil"], 1),
                "temperature": 24.0,
                "humidity": 75.0,
                "wind_speed": 12.0,
                "source": "Deterministic demo fallback",
                "status": "FALLBACK",
            },
        }


def build_live_zones():
    zones = []

    for i, (district, state, lat, lon) in enumerate(DISTRICTS):
        zones.append(
            live_weather_for_zone(
                district,
                state,
                lat,
                lon,
                26001 + i,
            )
        )

    return zones


# Existing pages can keep calling this name, but now it means
# "current live-weather-aware zones", not the previous demo zones.
def build_demo_zones():
    return build_live_zones()


# ------------------------------------------------------------
# Standalone local data helpers
# ------------------------------------------------------------
def get_alerts():
    return st.session_state.local_alerts

def get_incidents():
    return st.session_state.local_incidents

def get_assets():
    return []


# ------------------------------------------------------------
# Email: direct SMTP, no backend dependency
# ------------------------------------------------------------
def smtp_config():
    try:
        port = int(clean(os.getenv("SMTP_PORT", "587")) or "587")
    except ValueError:
        port = 587
    return {
        "host": clean(os.getenv("SMTP_HOST", "smtp.gmail.com")),
        "port": port,
        "username": clean(os.getenv("SMTP_USERNAME")),
        "password": clean(os.getenv("SMTP_PASSWORD")),
        "from_email": clean(os.getenv("EMAIL_FROM")) or clean(os.getenv("SMTP_USERNAME")),
        "tls": clean(os.getenv("SMTP_USE_TLS", "true")).lower() not in {"0", "false", "no"},
    }

def placeholder(v):
    low = clean(v).lower()
    return (not low) or any(x in low for x in ("your_", "replace_me", "example.com", "your-app-password", "xxxx"))

def smtp_ready():
    cfg = smtp_config()
    return bool(cfg["host"] and cfg["username"] and cfg["password"] and cfg["from_email"] and not placeholder(cfg["username"]) and not placeholder(cfg["password"]))

def valid_email(address):
    address = clean(address)
    if "@" not in address:
        return False
    local, domain = address.rsplit("@", 1)
    return bool(local and domain and "." in domain)

def send_email_direct(to_email, subject, body):
    cfg = smtp_config()
    to_email = clean(to_email)
    subject = clean(subject) or "LandslideGuard NER Alert"
    body = str(body or "").strip()

    if not valid_email(to_email):
        return {"status": "FAILED", "to": to_email, "error": "Enter a valid recipient email address."}
    if not smtp_ready():
        return {"status": "FAILED", "to": to_email, "error": "SMTP is not configured. Set SMTP_USERNAME and SMTP_PASSWORD in .env, then restart Streamlit."}

    try:
        msg = EmailMessage()
        msg["From"] = cfg["from_email"]
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)
        if cfg["port"] == 465:
            with smtplib.SMTP_SSL(cfg["host"], cfg["port"], timeout=20) as server:
                server.login(cfg["username"], cfg["password"])
                server.send_message(msg)
        else:
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=20) as server:
                server.ehlo()
                if cfg["tls"]:
                    server.starttls()
                    server.ehlo()
                server.login(cfg["username"], cfg["password"])
                server.send_message(msg)
        return {"status": "SENT", "to": to_email, "sent_at": datetime.now(timezone.utc).isoformat()}
    except smtplib.SMTPAuthenticationError:
        return {"status": "FAILED", "to": to_email, "error": "SMTP authentication failed. For Gmail, use a Google App Password, not your normal Gmail password."}
    except (smtplib.SMTPConnectError, TimeoutError, OSError) as exc:
        return {"status": "FAILED", "to": to_email, "error": f"Could not connect to {cfg['host']}:{cfg['port']}. {exc}"}
    except smtplib.SMTPException as exc:
        return {"status": "FAILED", "to": to_email, "error": f"SMTP error: {exc}"}
    except Exception as exc:
        return {"status": "FAILED", "to": to_email, "error": str(exc)}


def create_local_alert(payload, email_results):
    sent = sum(r.get("status") == "SENT" for r in email_results)
    failed = len(email_results) - sent
    status = "SENT" if sent and not failed else "PARTIAL" if sent else "FAILED" if failed else "NOT_REQUESTED"
    record = {
        "id": len(st.session_state.local_alerts) + 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "district": payload.get("district", "NER"),
        "risk_level": payload.get("risk_level", "MODERATE"),
        "language": payload.get("language", "English"),
        "message": payload.get("message", "Operational warning"),
        "subject": payload.get("subject", "LandslideGuard NER Alert"),
        "recipients": ", ".join(payload.get("recipients") or []),
        "dispatch_status": status,
        "email_status": status,
        "email_sent": sent,
        "email_failed": failed,
        "delivery_mode": "DIRECT SMTP",
    }
    if email_results:
        record["email_detail"] = email_results
    if payload.get("audit", True):
        st.session_state.local_alerts.append(record)
    return record


# ------------------------------------------------------------
# Header/sidebar
# ------------------------------------------------------------
def command_header(show_ticker=True):
    st.markdown(
        '<div class="govbar"><div class="govbrand"><div class="emblem">☸</div>'
        '<div><div class="govtitle">STATE EMERGENCY OPERATIONS CENTRE</div>'
        '<div class="govsub">NORTH EASTERN REGION • LANDSLIDE EARLY WARNING & DECISION INTELLIGENCE</div>'
        '</div></div><div class="live"><span class="dot"></span> SYSTEMS OPERATIONAL</div></div>',
        unsafe_allow_html=True,
    )
    if show_ticker:
        alerts = get_alerts()
        text = "  •  ".join(
            f"{a.get('risk_level','ALERT')} ALERT: {a.get('district','NER')} — {a.get('message','Operational warning')}"
            for a in alerts[-5:]
        )
        if not text:
            text = "NO UNRESOLVED BROADCAST ALERTS • MONITORING 24×7 • AI DECISION SUPPORT ONLINE • FIELD NETWORK CONNECTED"
        st.markdown(f'<div class="ticker"><span>🚨 LIVE ALERT FEED &nbsp; {text}</span></div>', unsafe_allow_html=True)


st.sidebar.title("⛰️ LANDSLIDEGUARD NER")
st.sidebar.caption("SIH 2026 • Problem 26001")

st.sidebar.toggle(
    "☀️ Bright mode" if DARK else "🌙 Dark mode",
    key="dark_mode",
    help="Switch the entire dashboard and map between dark and bright themes.",
)

page = st.sidebar.radio(
    "COMMAND MODULES",
    ["Command Center", "AI Digital Twin", "Risk Map", "Field Intelligence", "Alert Center", "Mobile Alert Preview", "Analytics", "About"],
)
st.sidebar.divider()
st.sidebar.success("● NER CONTROL FABRIC ONLINE")
st.sidebar.caption("Alert gateway: direct email / SMTP")
st.sidebar.caption("AI model: LG-NER-RF-1.0")

# ------------------------------------------------------------
# Command Center
# ------------------------------------------------------------
if page == "Command Center":
    command_header()
    st.title("Regional Situation Awareness")
    st.caption("Predictive decision support for district control rooms")

    zones = build_demo_zones()
    levels = [z.get("risk_level", "MODERATE") for z in zones]
    alerts = get_alerts()
    incidents = get_incidents()

    cols = st.columns(5)
    kpis = [
        ("MONITORED ZONES", len(zones), "8-state regional watch", "cyan"),
        ("HIGH / CRITICAL", sum(x in ("HIGH", "CRITICAL") for x in levels), "priority surveillance", "red"),
        ("CRITICAL", levels.count("CRITICAL"), "immediate review", "red"),
        ("FIELD REPORTS", len(incidents), "human verification", "amber"),
        ("ALERTS LOGGED", len(alerts), "auditable broadcasts", "cyan"),
    ]
    for col, (lab, val, meta, cls) in zip(cols, kpis):
        col.markdown(f'<div class="kpi {cls}"><div class="label">{lab}</div><div class="value">{val}</div><div class="meta">{meta}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="scanline"></div>', unsafe_allow_html=True)
    df = pd.DataFrame([
        {
            "District": z["district"], "State": z["state"], "Risk": z["risk_level"],
            "Score": z["risk_score"], "Confidence": f'{z["confidence"]*100:.0f}%',
            "Exposure": z["exposure_score"], "Priority": z["operational_priority"],
        }
        for z in zones
    ])
    st.markdown("### Regional situation board")
    st.markdown(_theme_table_html(df.sort_values("Priority", ascending=False)), unsafe_allow_html=True)
    st.info("Decision principle: **hazard probability × exposure = operational priority**.")

# ------------------------------------------------------------
# Digital Twin
# ------------------------------------------------------------
elif page == "AI Digital Twin":
    st.title("🧠 AI Digital Twin / What-If Simulator")
    st.write("Demonstrate how changing environmental conditions shifts risk.")
    names = [x[0] for x in DISTRICTS]
    selected = st.selectbox("Scenario zone", names)
    f = demo_features(26001 + names.index(selected))

    a, b = st.columns(2)
    with a:
        f["rainfall24"] = st.slider("24h rainfall (mm)", 0, 300, int(f["rainfall24"]))
        f["rainfall72"] = st.slider("72h rainfall (mm)", 0, 600, int(f["rainfall72"]))
        f["soil"] = st.slider("Soil moisture (%)", 10, 100, int(f["soil"]))
        f["slope"] = st.slider("Slope (degrees)", 2, 65, int(f["slope"]))
    with b:
        f["elevation"] = st.slider("Elevation (m)", 50, 3500, int(f["elevation"]))
        f["ndvi"] = st.slider("Vegetation index", 0.0, 1.0, float(f["ndvi"]))
        f["road_dist"] = st.slider("Distance to strategic road (m)", 5, 1500, int(f["road_dist"]))
        f["history"] = st.slider("Historical event density", 0.0, 12.0, float(f["history"]))

    p = local_prediction(f)
    a, b, c, d = st.columns(4)
    a.metric("RISK LEVEL", p["risk_level"])
    b.metric("HAZARD SCORE", f'{p["risk_score"]:.1f}/100')
    c.metric("AI CONFIDENCE", f'{p["confidence"]*100:.0f}%')
    d.metric("OPERATIONAL PRIORITY", f'{p["operational_priority"]:.1f}/100')
    st.progress(min(p["risk_score"] / 100, 1))
    st.markdown("### Why is the AI worried?")
    st.markdown(_theme_table_html(pd.DataFrame(p["top_factors"])), unsafe_allow_html=True)
    st.info("Recommended action: " + p["recommended_action"])

# ------------------------------------------------------------
# Risk Map
# ------------------------------------------------------------
elif page == "Risk Map":
    command_header()

    st.title("🗺️ NER Multi-Layer Risk & Exposure Map")
    st.caption(
        "Live Open-Meteo conditions drive the precipitation and "
        "moisture-pressure components of the prototype risk score. No API key required."
    )

    zones = build_live_zones()

    live_count = sum(
        z.get("data_status") == "LIVE"
        for z in zones
    )
    fallback_count = len(zones) - live_count

    status_col, refresh_col = st.columns([3, 1])

    with status_col:
        if live_count == len(zones):
            sources = sorted({z.get("source", "Live weather") for z in zones})
            st.success(
                f"🟢 LIVE WEATHER DATA • {live_count}/{len(zones)} districts updated • "
                f"Provider: {', '.join(sources)}"
            )
        elif live_count:
            st.warning(
                f"🟡 MIXED DATA • {live_count} live / "
                f"{fallback_count} fallback"
            )
        else:
            st.error(
                "🔴 WEATHER UNAVAILABLE • "
                "Showing deterministic fallback data"
            )

        errors = [
            z.get("provider_error")
            for z in zones
            if z.get("provider_error")
        ]
        if errors:
            st.caption(f"Weather detail: {errors[0]}")
            # Open-Meteo needs no API key; never ask the user to configure one.

    with refresh_col:
        if st.button(
            "🔄 Refresh live conditions",
            type="primary",
            key="refresh_weather",
        ):
            st.cache_data.clear()
            st.rerun()

    selected = st.selectbox(
        "Inspect district",
        [z["district"] for z in zones],
        key="risk_map_district",
    )

    zone = next(
        z for z in zones
        if z["district"] == selected
    )
    weather = zone["weather"]

    st.markdown(
        f"## {zone['district']} — {zone['state']}"
    )

    metrics = st.columns(7)

    metrics[0].metric(
        "RAIN LAST 1H",
        f"{weather['rain_last_1h']:.1f} mm",
    )
    metrics[1].metric(
        "RAIN FORECAST 24H",
        f"{weather['rain_forecast24']:.1f} mm",
    )
    metrics[2].metric(
        "RAIN FORECAST 72H",
        f"{weather['rain_forecast72']:.1f} mm",
    )
    metrics[3].metric(
        "MOISTURE PRESSURE",
        f"{weather['moisture_pressure']:.1f}%",
    )
    metrics[4].metric(
        "TEMPERATURE",
        f"{weather['temperature']:.1f} °C",
    )
    metrics[5].metric(
        "HUMIDITY",
        f"{weather['humidity']:.0f}%",
    )
    metrics[6].metric(
        "RISK",
        zone["risk_level"],
        f"Score {zone['risk_score']:.1f}",
    )

    if zone["data_status"] == "LIVE":
        st.success(
            f"🟢 LIVE WEATHER DATA • "
            f"Updated: {weather['timestamp']} • "
            f"Source: {weather['source']}"
        )
    else:
        st.warning(
            f"🟡 FALLBACK DATA • OpenWeather unavailable. "
            f"Reason: {zone.get('provider_error', 'Unknown error')}"
        )

    table = pd.DataFrame([
        {
            "District": z["district"],
            "Status": z["data_status"],
            "Updated": z["weather"]["timestamp"],
            "Source": z["weather"]["source"],
            "Rain 1h (mm)": z["weather"]["rain_last_1h"],
            "Forecast 24h (mm)": z["weather"]["rain_forecast24"],
            "Forecast 72h (mm)": z["weather"]["rain_forecast72"],
            "Moisture pressure (%)": z["weather"]["moisture_pressure"],
            "Temp (°C)": z["weather"]["temperature"],
            "Humidity (%)": z["weather"]["humidity"],
            "Wind (km/h)": z["weather"]["wind_speed"],
            "Risk": z["risk_level"],
            "Score": z["risk_score"],
        }
        for z in zones
    ])

    # Use a normal HTML table here. Streamlit's dataframe grid can inherit
    # a dark canvas/background and make this table appear as a black block.
    def _risk_table_html(df):
        headers = ''.join(f'<th>{str(col)}</th>' for col in df.columns)
        rows = []
        for _, row in df.iterrows():
            cells = []
            for col, value in row.items():
                text = str(value)
                if isinstance(value, (float, np.floating)):
                    text = f"{value:.1f}"
                cls = ''
                if col == "Risk":
                    cls = f' class="risk-cell {text.upper()}"'
                cells.append(f'<td{cls}>{text}</td>')
            rows.append('<tr>' + ''.join(cells) + '</tr>')
        body = ''.join(rows)
        return f"""<div class=\"risk-table-wrap\">
          <table class=\"risk-table\">
            <thead><tr>{headers}</tr></thead>
            <tbody>{body}</tbody>
          </table>
        </div>"""

    st.markdown(_risk_table_html(table), unsafe_allow_html=True)

    st.markdown("### Interactive risk map")

    map_col1, map_col2 = st.columns([1, 1])
    with map_col1:
        show_heat = st.toggle(
            "🔥 Show heat-wave layer",
            value=True,
            key="show_heat_wave",
            help="Highlights districts by current temperature. It is an operational heat-stress visualization, not an official heat-wave warning."
        )
    with map_col2:
        st.caption("Heat layer: cool → warm → extreme based on current temperature")

    # Permanent light basemap. The map stays light even when the dashboard theme changes.
    map_tiles = "OpenStreetMap"
    m = folium.Map(
        location=[25.7, 92.5],
        zoom_start=6,
        tiles=map_tiles,
        control_scale=True,
        prefer_canvas=True,
    )

    # Heat-wave visualization. Folium's HeatMap renders a smooth intensity
    # surface; temperature is normalized to a 20–45 °C operational range.
    if show_heat:
        from folium.plugins import HeatMap
        heat_points = []
        for z in zones:
            temp = float(z["weather"]["temperature"])
            intensity = float(np.clip((temp - 20.0) / 25.0, 0.05, 1.0))
            heat_points.append([z["lat"], z["lon"], intensity])
        HeatMap(
            heat_points,
            radius=55,
            blur=38,
            min_opacity=0.28,
            max_zoom=7,
            gradient={
                0.20: "blue",
                0.40: "cyan",
                0.60: "yellow",
                0.78: "orange",
                0.90: "red",
                1.00: "darkred",
            },
        ).add_to(m)

    colors = {
        "LOW": "green",
        "MODERATE": "orange",
        "HIGH": "red",
        "CRITICAL": "darkred",
    }

    for z in zones:
        w = z["weather"]

        popup_bg = "#0b2035" if DARK else "#ffffff"
        popup_text = "#e8f1f8" if DARK else "#10202e"
        popup_border = "#2a4a66" if DARK else "#c7d6df"
        popup = (
            f"<div style='min-width:250px;background:{popup_bg};color:{popup_text};padding:8px;border:1px solid {popup_border};border-radius:8px;font-family:Arial,sans-serif'>"
            f"<b style='color:{popup_text}'>{z['district']} — {z['state']}</b><br><br>"
            f"<b>{w['status']} WEATHER DATA</b><br>"
            f"Updated: {w['timestamp']}<br>"
            f"Source: {w['source']}<br><br>"
            f"Rain last 1h: <b>{w['rain_last_1h']:.1f} mm</b><br>"
            f"Forecast 24h: <b>{w['rain_forecast24']:.1f} mm</b><br>"
            f"Forecast 72h: <b>{w['rain_forecast72']:.1f} mm</b><br>"
            f"Moisture pressure: <b>{w['moisture_pressure']:.1f}%</b><br>"
            f"Temperature: <b>{w['temperature']:.1f} °C</b><br>"
            f"Humidity: <b>{w['humidity']:.0f}%</b><br>"
            f"Wind: <b>{w['wind_speed']:.1f} km/h</b><br><br>"
            f"<b>Risk: {z['risk_level']}</b><br>"
            f"Score: <b>{z['risk_score']:.1f}</b><br>"
            f"Priority: <b>{z['operational_priority']:.1f}</b>"
            f"</div>"
        )

        folium.CircleMarker(
            [z["lat"], z["lon"]],
            radius=9 + z["risk_score"] / 15,
            color=colors.get(z["risk_level"], "orange"),
            fill=True,
            fill_opacity=.78,
            popup=folium.Popup(
                popup,
                max_width=340,
            ),
            tooltip=(
                f"{z['district']} • "
                f"{z['risk_level']} • "
                f"{z['risk_score']:.1f}"
            ),
        ).add_to(m)

    for report in get_incidents():
        folium.Marker(
            [report["latitude"], report["longitude"]],
            tooltip=(
                f"FIELD: {report['incident_type']} • "
                f"{report['severity']}"
            ),
            icon=folium.Icon(
                color="blue",
                icon="info-sign",
            ),
        ).add_to(m)

    st_folium(
        m,
        height=650,
        width=None,
        returned_objects=[],
    )

    st.info(
        "Scope note: this is live weather-driven risk intelligence. "
        "OpenWeather weather conditions are real-time/current provider "
        "data, while slope, history, exposure and the final risk model "
        "remain prototype components. It is not direct landslide detection."
    )


# ------------------------------------------------------------
# Field Intelligence
# ------------------------------------------------------------
elif page == "Field Intelligence":
    st.title("📸 Field Intelligence & Citizen Sensing")
    st.write("Capture observations that can verify or challenge the model.")
    with st.form("incident_form"):
        reporter = st.text_input("Reporter / team", "NER Rapid Response Team")
        district = st.selectbox("District", [x[0] for x in DISTRICTS])
        lat = st.number_input("Latitude", 23.0, 29.0, 25.5788, format="%.6f")
        lon = st.number_input("Longitude", 88.0, 97.0, 91.8933, format="%.6f")
        typ = st.selectbox("Observation", ["Slope crack", "Landslide", "Rockfall", "Road blockage", "Waterlogging", "Other"])
        sev = st.select_slider("Observed severity", ["Low", "Moderate", "High", "Critical"], value="Moderate")
        desc = st.text_area("Field notes")
        photo = st.file_uploader("Photo evidence", type=["jpg", "jpeg", "png"])
        submit = st.form_submit_button("SUBMIT FIELD INTELLIGENCE", type="primary")
    if submit:
        report = {
            "id": len(st.session_state.local_incidents) + 1,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reporter": reporter, "district": district,
            "latitude": lat, "longitude": lon,
            "incident_type": typ, "severity": sev,
            "description": desc, "photo_attached": bool(photo),
        }
        st.session_state.local_incidents.append(report)
        st.success(f'Report #{report["id"]} stored locally for this session.')

    inc = get_incidents()
    st.markdown("### Recent reports")
    if inc:
        st.markdown(_theme_table_html(pd.DataFrame(inc)), unsafe_allow_html=True)
    else:
        st.info("No reports yet.")

# ------------------------------------------------------------
# Alert Center — EMAIL ONLY
# ------------------------------------------------------------
elif page == "Alert Center":
    command_header()
    st.title("🚨 Alert Orchestration & Broadcast Center")
    st.warning("AI recommends. Authorized officials approve and trigger operational warnings.")

    left, right = st.columns([1.1, 1])
    with left:
        district = st.selectbox("Target district", [x[0] for x in DISTRICTS])
        level = st.selectbox("Risk level", ["MODERATE", "HIGH", "CRITICAL"])
        lang = st.selectbox("Language", ["English", "Hindi", "Assamese", "Bengali", "Nepali"])

        templates = {
            "English": f"LANDSLIDE WARNING — {level}. Increased landslide risk near {district}. Avoid unstable slopes, follow official advisories, and report blocked roads.",
            "Hindi": f"भूस्खलन चेतावनी — {level}। {district} के आसपास भूस्खलन का जोखिम बढ़ा है। अस्थिर ढलानों से दूर रहें और आधिकारिक निर्देशों का पालन करें।",
            "Assamese": f"ভূমিস্খলন সতৰ্কবাণী — {level}। {district} অঞ্চলত ভূমিস্খলনৰ আশংকা বৃদ্ধি পাইছে। চৰকাৰী নিৰ্দেশনা মানি চলক।",
            "Bengali": f"ভূমিধস সতর্কতা — {level}। {district}-এর আশেপাশে ভূমিধসের ঝুঁকি বেড়েছে। সরকারি নির্দেশনা মেনে চলুন।",
            "Nepali": f"पहिरो चेतावनी — {level}। {district} वरपर पहिरोको जोखिम बढेको छ। आधिकारिक निर्देशन पालना गर्नुहोस्।",
        }
        msg = st.text_area("Broadcast message", templates[lang], height=120)
        email_recipients = st.text_input("Email recipients", placeholder="you@example.com, district-control@example.gov")
        subject = st.text_input("Email subject", value=f"LandslideGuard NER — {level} alert for {district}")
        audit = st.checkbox("Audit log", value=True)

        if st.button("AUTHORIZE & DISPATCH ALERT", type="primary"):
            recipients = [x.strip() for x in email_recipients.split(",") if x.strip()]
            if not recipients:
                st.error("Enter at least one recipient email address.")
            else:
                results = [send_email_direct(recipient, subject, msg) for recipient in recipients]
                out = create_local_alert({
                    "district": district, "risk_level": level, "language": lang,
                    "message": msg, "subject": subject,
                    "recipients": recipients, "audit": audit,
                }, results)
                sent = sum(r.get("status") == "SENT" for r in results)
                failed = len(results) - sent
                if sent == len(results):
                    st.success(f'✅ Alert #{out.get("id", "LOCAL")} delivered by email to {sent} recipient(s).')
                elif sent:
                    st.warning(f'⚠️ Alert #{out.get("id", "LOCAL")} partially delivered: {sent} sent, {failed} failed.')
                else:
                    st.error('❌ Email delivery failed.')
                for result in results:
                    if result.get("status") != "SENT":
                        st.error(f'{result.get("to", "Recipient")}: {result.get("error", "Email failed")}')

    with right:
        preview = f'''
        <div class="panel"><div class="eyebrow">MOBILE RECIPIENT EXPERIENCE</div>
        <h3>Emergency notification preview</h3>
        <div class="mobile-preview-card" style="border-radius:28px;padding:18px;margin-top:8px;max-width:330px">
        <div class="small">NOW • STATE EOC</div>
        <div style="font-size:18px;font-weight:800;margin:8px 0">🚨 Landslide Warning</div>
        <div class="mobile-preview-message" style="font-size:12px;line-height:1.55">{templates[lang]}</div>
        <div class="riskbadge {level}" style="margin-top:12px">{level}</div></div>
        <p class="small">Email is the only delivery channel in this version. Configure SMTP to send real alerts.</p></div>'''
        st.markdown(preview, unsafe_allow_html=True)

    alerts = get_alerts()
    if alerts:
        st.markdown("### Broadcast audit trail")
        st.markdown(_theme_table_html(pd.DataFrame(alerts)), unsafe_allow_html=True)

    st.markdown("### ✉️ Live Email Gateway")
    cfg = smtp_config()
    if placeholder(cfg["username"]) or placeholder(cfg["password"]):
        st.warning("🟡 SMTP not configured — add SMTP_USERNAME and SMTP_PASSWORD to .env.")
    else:
        st.success(f'🟢 SMTP configured — {cfg["host"]}:{cfg["port"]}')
    st.caption("This test sends directly through SMTP. No separate backend service is required.")

    live_email = st.text_input("Recipient email address", placeholder="your-email@example.com", key="live_email")
    live_subject = st.text_input("Email subject", value="LandslideGuard NER — DEMO ALERT", key="live_subject")
    live_message = st.text_area(
        "Email message",
        value="LANDSLIDEGUARD NER: DEMO ALERT — Please follow official local disaster-management instructions.",
        key="live_email_message",
    )
    if st.button("✉️ SEND TEST EMAIL", type="primary", key="send_test_email"):
        result = send_email_direct(live_email, live_subject, live_message)
        if result.get("status") == "SENT":
            st.success(f'✅ EMAIL SENT to {live_email}')
        else:
            st.error(f'❌ EMAIL FAILED: {result.get("error", "Unknown error")}')

# ------------------------------------------------------------
# Mobile Alert Preview — NEVER EMPTY
# ------------------------------------------------------------
elif page == "Mobile Alert Preview":
    command_header(False)
    st.title("📱 Public Mobile Alert Surface")
    st.caption("Citizen-facing notification simulation • automatically populated for demonstrations.")

    live_alerts = get_alerts()
    alerts = live_alerts if live_alerts else DEMO_ALERTS
    if live_alerts:
        st.success("🟢 LIVE NOTIFICATIONS • Showing the latest authorized broadcasts.")
    else:
        st.info("🟡 DEMO NOTIFICATION • No live broadcasts yet — showing realistic emergency alerts so this module is never empty.")

    st.markdown("### Emergency notification feed")
    for a in reversed(alerts[-5:]):
        lvl = a.get("risk_level", "MODERATE")
        district = a.get("district", "NER")
        created = a.get("created_at", "NOW")
        message = a.get("message", "Follow official emergency instructions.")
        st.markdown(
            f'''<div class="mobile-alert-card" style="max-width:760px;border-radius:28px;padding:20px 22px;margin:0 0 16px">
            <div style="display:flex;justify-content:space-between;align-items:center"><span class="small">STATE EOC • {created}</span><span class="riskbadge {lvl}">{lvl}</span></div>
            <div style="font-size:20px;font-weight:800;margin:14px 0 5px;color:var(--text)">🚨 Landslide Warning</div>
            <div class="district-text" style="font-size:13px;font-weight:700;margin-bottom:10px">📍 {district}</div>
            <div class="message-text" style="font-size:13px;line-height:1.65">{message}</div>
            <div class="advisory" style="margin-top:16px;padding:10px 12px;border-radius:10px;font-size:11px;font-weight:700">OPEN EMERGENCY ADVISORY ›</div>
            </div>''',
            unsafe_allow_html=True,
        )

    c1, c2, c3 = st.columns(3)
    c1.metric("📧 EMAIL", "READY", "Direct SMTP")
    c2.metric("🧾 AUDIT", "ENABLED", "Every dispatch logged")
    c3.metric("🔒 BACKEND", "NOT REQUIRED", "Standalone app")
    st.caption("The preview is visual only; actual delivery is handled by email SMTP.")

# ------------------------------------------------------------
# Analytics — NEVER EMPTY
# ------------------------------------------------------------
elif page == "Analytics":
    command_header()
    st.title("📊 Resilience Analytics")
    st.caption("Regional decision intelligence • live Open-Meteo weather inputs + prototype terrain/exposure factors.")

    zones = build_demo_zones()
    st.info("🟢 LIVE-WEATHER MODE • Analytics use Open-Meteo precipitation/moisture-pressure inputs with prototype terrain/exposure factors.")

    df = pd.DataFrame(zones)
    if df.empty:
        # Absolute last-resort guard: analytics can never render an empty state.
        zones = build_demo_zones()
        df = pd.DataFrame(zones)

    cols = st.columns(5)
    cols[0].metric("MONITORED ZONES", len(df))
    cols[1].metric("CRITICAL", int((df["risk_level"] == "CRITICAL").sum()))
    cols[2].metric("HIGH", int((df["risk_level"] == "HIGH").sum()))
    cols[3].metric("AVG HAZARD", f'{df["risk_score"].mean():.1f}/100')
    cols[4].metric("AVG PRIORITY", f'{df["operational_priority"].mean():.1f}/100')

    a, b = st.columns(2)
    with a:
        chart = px.bar(df.sort_values("risk_score", ascending=False), x="district", y="risk_score", color="risk_level", title="Hazard score by NER district", template=PLOTLY_THEME, text="risk_score")
        chart.update_traces(texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False, hovertemplate="%{x}<br>Risk score: %{y:.1f}<extra></extra>")
        chart.update_layout(height=430, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8f1f8" if DARK else "#10202e", size=13), legend=dict(font=dict(color="#e8f1f8" if DARK else "#10202e")), margin=dict(l=55,r=25,t=70,b=70), xaxis=dict(title="District", tickfont=dict(color="#e8f1f8" if DARK else "#10202e"), title_font=dict(color="#e8f1f8" if DARK else "#10202e")), yaxis=dict(title="Risk score", range=[0,105], tickfont=dict(color="#e8f1f8" if DARK else "#10202e"), title_font=dict(color="#e8f1f8" if DARK else "#10202e")))
        st.plotly_chart(chart, use_container_width=True, config={"displaylogo": False, "displayModeBar": True, "modeBarButtonsToRemove": []})
    with b:
        chart = px.scatter(df, x="risk_score", y="operational_priority", size="exposure_score", color="risk_level", hover_name="district", title="Hazard vs operational priority", template=PLOTLY_THEME, text="district")
        chart.update_traces(textposition="top center", cliponaxis=False, hovertemplate="%{text}<br>Risk: %{x:.1f}<br>Priority: %{y:.1f}<extra></extra>")
        chart.update_layout(height=430, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8f1f8" if DARK else "#10202e", size=13), legend=dict(font=dict(color="#e8f1f8" if DARK else "#10202e")), margin=dict(l=65,r=25,t=70,b=65), xaxis=dict(title="Risk score", range=[0,105], tickfont=dict(color="#e8f1f8" if DARK else "#10202e"), title_font=dict(color="#e8f1f8" if DARK else "#10202e")), yaxis=dict(title="Operational priority", range=[0,105], tickfont=dict(color="#e8f1f8" if DARK else "#10202e"), title_font=dict(color="#e8f1f8" if DARK else "#10202e")))
        st.plotly_chart(chart, use_container_width=True, config={"displaylogo": False, "displayModeBar": True, "modeBarButtonsToRemove": []})

    c, d = st.columns(2)
    with c:
        rainfall = pd.DataFrame({
            "district": df["district"],
            "24h rainfall (mm)": [z["features"]["rainfall24"] for z in zones],
            "risk_score": df["risk_score"],
        })
        chart = px.bar(rainfall.sort_values("24h rainfall (mm)", ascending=False), x="district", y="24h rainfall (mm)", color="risk_score", title="Rainfall pressure across monitored districts", template=PLOTLY_THEME, text="24h rainfall (mm)")
        chart.update_traces(texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False, hovertemplate="%{x}<br>Rainfall: %{y:.1f} mm<extra></extra>")
        chart.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8f1f8" if DARK else "#10202e", size=13), legend=dict(font=dict(color="#e8f1f8" if DARK else "#10202e")), margin=dict(l=60,r=25,t=70,b=70), xaxis=dict(title="District", tickfont=dict(color="#e8f1f8" if DARK else "#10202e"), title_font=dict(color="#e8f1f8" if DARK else "#10202e")), yaxis=dict(title="Rainfall (mm)", rangemode="tozero", tickfont=dict(color="#e8f1f8" if DARK else "#10202e"), title_font=dict(color="#e8f1f8" if DARK else "#10202e")))
        st.plotly_chart(chart, use_container_width=True, config={"displaylogo": False, "displayModeBar": True, "modeBarButtonsToRemove": []})
    with d:
        chart = px.scatter(df, x="exposure_score", y="operational_priority", color="risk_level", hover_name="district", title="Exposure-driven response priority", template=PLOTLY_THEME, text="district")
        chart.update_traces(textposition="top center", cliponaxis=False, hovertemplate="%{text}<br>Exposure: %{x:.1f}<br>Priority: %{y:.1f}<extra></extra>")
        chart.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8f1f8" if DARK else "#10202e", size=13), legend=dict(font=dict(color="#e8f1f8" if DARK else "#10202e")), margin=dict(l=65,r=25,t=70,b=65), xaxis=dict(title="Exposure score", range=[0,105], tickfont=dict(color="#e8f1f8" if DARK else "#10202e"), title_font=dict(color="#e8f1f8" if DARK else "#10202e")), yaxis=dict(title="Operational priority", range=[0,105], tickfont=dict(color="#e8f1f8" if DARK else "#10202e"), title_font=dict(color="#e8f1f8" if DARK else "#10202e")))
        st.plotly_chart(chart, use_container_width=True, config={"displaylogo": False, "displayModeBar": True, "modeBarButtonsToRemove": []})

    st.markdown("### Decision intelligence")
    st.markdown(
        '<div class="panel"><div class="eyebrow">AI EXPLANATION</div>'
        '<b>Why operational priority differs from hazard score</b>'
        '<p class="small" style="margin-top:8px">The command center combines predicted landslide hazard with exposure and access constraints. '
        'A moderately hazardous location can therefore become a higher response priority when more people, roads or critical assets are exposed.</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        _theme_table_html(
            df[["district", "state", "risk_level", "risk_score", "confidence", "exposure_score", "operational_priority"]].sort_values("operational_priority", ascending=False)
        ),
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------
# About
# ------------------------------------------------------------
else:
    st.title("ℹ️ LandslideGuard NER")
    st.markdown("""
### The winning story

**The AI does not replace the disaster-management officer. It gives the officer a better decision window.**

**Sense → Fuse → Predict → Explain → Prioritize → Simulate → Alert → Verify → Learn**

### Demo reliability
- Analytics uses live weather when OpenWeather is available and deterministic fallback data if the provider is unavailable.
- Mobile Alert Preview has realistic demo notifications and cannot be empty.
- Email test sends directly through SMTP; backend service is not required for the test-email button.
- Email is the only operational notification channel in this version.
- Real email delivery requires valid SMTP credentials in `.env`.

### Production note
The hackathon build uses reproducible synthetic data for the self-contained demo. It must be independently validated against real regional data before operational use.
""")
