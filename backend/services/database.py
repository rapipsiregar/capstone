import os
import sqlite3
from typing import Dict, Any, List


DEFAULT_DB_PATH = "data/history.db"


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Establishes connection to SQLite database and sets row factory."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initializes SQLite database tables for storing review inference logs."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS review_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_text TEXT NOT NULL,
        cleaned_text TEXT NOT NULL,
        predicted_aspect TEXT NOT NULL,
        aspect_confidence REAL NOT NULL,
        predicted_trust TEXT NOT NULL,
        trust_confidence REAL NOT NULL,
        model_type TEXT NOT NULL,
        execution_time_ms REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()


def save_review_log(data: Dict[str, Any], db_path: str = DEFAULT_DB_PATH) -> int:
    """Inserts a review inference log record into SQLite database."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO review_logs (
        raw_text, cleaned_text, predicted_aspect, aspect_confidence,
        predicted_trust, trust_confidence, model_type, execution_time_ms
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(data.get("raw_text", "")),
        str(data.get("cleaned_text", "")),
        str(data.get("predicted_aspect", "")),
        float(data.get("aspect_confidence", 0.0)),
        str(data.get("predicted_trust", "")),
        float(data.get("trust_confidence", 0.0)),
        str(data.get("model_type", "")),
        float(data.get("execution_time_ms", 0.0))
    ))

    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id


def get_recent_logs(limit: int = 50, offset: int = 0, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves the most recent review inference logs with pagination support."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, raw_text, cleaned_text, predicted_aspect, aspect_confidence,
           predicted_trust, trust_confidence, model_type, execution_time_ms, created_at
    FROM review_logs
    ORDER BY id DESC
    LIMIT ? OFFSET ?
    """, (limit, offset))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_total_logs_count(db_path: str = DEFAULT_DB_PATH) -> int:
    """Returns the total number of review logs stored in the database."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM review_logs;")
    total = cursor.fetchone()["total"]
    conn.close()
    return int(total)


def get_analytics_summary(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Calculates summary statistics of reviews logged in SQLite database."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM review_logs;")
    total_reviews = cursor.fetchone()["total"]

    cursor.execute("SELECT predicted_aspect, COUNT(*) as count FROM review_logs GROUP BY predicted_aspect;")
    aspect_rows = cursor.fetchall()
    aspect_counts = {row["predicted_aspect"]: row["count"] for row in aspect_rows}

    cursor.execute("SELECT predicted_trust, COUNT(*) as count FROM review_logs GROUP BY predicted_trust;")
    trust_rows = cursor.fetchall()
    trust_counts = {row["predicted_trust"]: row["count"] for row in trust_rows}

    cursor.execute("SELECT AVG(execution_time_ms) as avg_latency FROM review_logs;")
    avg_latency = cursor.fetchone()["avg_latency"] or 0.0

    conn.close()
    return {
        "total_reviews": total_reviews,
        "aspect_counts": aspect_counts,
        "trust_counts": trust_counts,
        "avg_execution_time_ms": round(float(avg_latency), 2)
    }
