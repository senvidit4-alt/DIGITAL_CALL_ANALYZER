"""
database.py — SQLite persistence layer for MCA Cyber Dost
All analysis results are stored here so /stats never resets on restart.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cyber_dost.db")


def get_db():
    """Return a DB connection with Row factory (dict-like access)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist. Safe to call on every startup."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS analyses (
            id          INTEGER  PRIMARY KEY AUTOINCREMENT,
            input_text  TEXT,
            transcript  TEXT,
            score       REAL     NOT NULL,
            verdict     TEXT     NOT NULL,
            stage       TEXT,
            source      TEXT     DEFAULT 'text',
            timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id          INTEGER  PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER  REFERENCES analyses(id),
            is_correct  INTEGER  NOT NULL,
            comment     TEXT,
            timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("✅ Database ready.")


def save_analysis(input_text: str, score: float, verdict: str, stage: str,
                  transcript: str = None, source: str = "text") -> int:
    """Persist one analysis result; returns the new row id."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO analyses (input_text, transcript, score, verdict, stage, source)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (input_text, transcript, score, verdict, stage, source),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def get_stats() -> dict:
    """Return aggregate counts from DB."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM analyses")
    total = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS scams FROM analyses WHERE verdict = 'SCAM'")
    scams = cur.fetchone()["scams"]
    conn.close()
    return {"total_analyzed": total, "scams_flagged": scams}


def get_history(limit: int = 20) -> list:
    """Return the last N analyses as a list of dicts."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """SELECT id, input_text, transcript, score, verdict, stage, source, timestamp
           FROM analyses ORDER BY id DESC LIMIT ?""",
        (limit,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def save_feedback(analysis_id: int, is_correct: bool, comment: str = None) -> int:
    """Persist user feedback for an analysis result; returns feedback row id."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO feedback (analysis_id, is_correct, comment) VALUES (?, ?, ?)",
        (analysis_id, int(is_correct), comment),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id
