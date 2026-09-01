import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "landslideguard.db"
UPLOAD_DIR = DB_PATH.parent / "uploads"
DB_PATH.parent.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = connect()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS incidents(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        reporter TEXT,
        district TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        incident_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        description TEXT,
        photo_path TEXT,
        visual_quality REAL DEFAULT 0,
        triage_label TEXT DEFAULT 'UNASSESSED'
    );

    CREATE TABLE IF NOT EXISTS alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        district TEXT NOT NULL,
        risk_level TEXT NOT NULL,
        language TEXT NOT NULL,
        message TEXT NOT NULL,
        acknowledged INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        district TEXT NOT NULL,
        risk_level TEXT NOT NULL,
        risk_score REAL NOT NULL,
        confidence REAL NOT NULL,
        exposure_score REAL NOT NULL,
        operational_priority REAL NOT NULL,
        features_json TEXT NOT NULL
    );
    """)
    # Lightweight migration for older demo databases.
    existing = {row[1] for row in con.execute("PRAGMA table_info(alerts)").fetchall()}
    for name, sql_type in (("email_status", "TEXT DEFAULT 'disabled'"), ("email_sent", "INTEGER DEFAULT 0"), ("email_detail", "TEXT DEFAULT ''")):
        if name not in existing:
            con.execute(f"ALTER TABLE alerts ADD COLUMN {name} {sql_type}")
    con.commit()
    con.close()

def insert_incident(values):
    con = connect()
    cur = con.execute("""
        INSERT INTO incidents
        (created_at,reporter,district,latitude,longitude,incident_type,severity,
         description,photo_path,visual_quality,triage_label)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)
    """, values)
    con.commit()
    row_id = cur.lastrowid
    con.close()
    return row_id

def insert_alert(values):
    con = connect()
    cur = con.execute("""
        INSERT INTO alerts(created_at,district,risk_level,language,message)
        VALUES(?,?,?,?,?)
    """, values)
    con.commit()
    row_id = cur.lastrowid
    con.close()
    return row_id

def insert_prediction(values):
    con = connect()
    con.execute("""
        INSERT INTO predictions
        (created_at,district,risk_level,risk_score,confidence,exposure_score,
         operational_priority,features_json)
        VALUES(?,?,?,?,?,?,?,?)
    """, values)
    con.commit()
    con.close()

def rows(table, limit=100):
    con = connect()
    out = [dict(r) for r in con.execute(
        f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()]
    con.close()
    return out
