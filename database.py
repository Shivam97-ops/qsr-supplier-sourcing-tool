# database.py
# Handles all interactions with the local SQLite database (suppliers.db).
# SQLite is a lightweight database stored as a single file — no server needed.
#
# WHAT'S NEW IN THIS VERSION:
#   - migrate_db() adds new columns: supplier_class, risk_score, risk_level,
#     risk_data, logistics_data, landed_cost_data, origin_country.
#   - save_supplier() stores all new fields including JSON blobs for
#     risk_data, logistics_data, and landed_cost_data.
#   - get_all_scorecards() now also returns score, risk_level, and
#     total landed cost for the upgraded comparison table.

import sqlite3
import json
import pandas as pd
from datetime import datetime

DB_PATH = "suppliers.db"


# ─────────────────────────────────────────────────────────────────────────────
# SETUP & MIGRATION
# ─────────────────────────────────────────────────────────────────────────────

def init_db():
    """
    Creates the database tables if they do not already exist.
    Safe to call on every app startup — CREATE TABLE IF NOT EXISTS is a no-op
    when the table already exists.
    """
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            website       TEXT,
            location      TEXT,
            contact_info  TEXT,
            product       TEXT,
            supplier_type TEXT,
            summary       TEXT,
            strengths     TEXT,
            saved_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scorecards (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id        INTEGER NOT NULL,
            price_score        INTEGER,
            lead_time_score    INTEGER,
            reliability_score  INTEGER,
            notes              TEXT,
            rated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def migrate_db():
    """
    Adds new columns to an existing suppliers table without destroying saved data.

    Each ALTER TABLE call is wrapped in a try/except so it silently skips columns
    that already exist. This means migrate_db() is always safe to call at startup.
    """
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # (column_name, SQL type + default)
    new_columns = [
        # Phase 1 columns (original)
        ("score",           "INTEGER DEFAULT 0"),
        ("certifications",  "TEXT DEFAULT '[]'"),
        ("moq",             "TEXT"),
        ("lead_time",       "TEXT"),
        ("risk_flags",      "TEXT DEFAULT '[]'"),
        ("qsr_category",    "TEXT"),
        ("product_match",   "TEXT"),            # legacy compatibility

        # Phase 2 columns (new in this upgrade)
        ("supplier_class",  "TEXT DEFAULT 'Distributor'"),   # Manufacturer / Distributor / Trader/Broker / Local Vendor
        ("origin_country",  "TEXT"),                          # Country name only
        ("risk_score",      "INTEGER DEFAULT 0"),             # 0-100 overall risk (higher = riskier)
        ("risk_level",      "TEXT DEFAULT 'Unknown'"),        # Low / Medium / High
        ("risk_data",       "TEXT DEFAULT '{}'"),             # JSON: full 3-category risk breakdown
        ("logistics_data",  "TEXT DEFAULT '{}'"),             # JSON: all logistics mode options
        ("landed_cost_data","TEXT DEFAULT '{}'"),             # JSON: full landed cost breakdown
    ]

    for col_name, col_def in new_columns:
        try:
            cursor.execute(f"ALTER TABLE suppliers ADD COLUMN {col_name} {col_def}")
        except sqlite3.OperationalError:
            pass  # Column already exists — skip silently

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# SAVE & RETRIEVE
# ─────────────────────────────────────────────────────────────────────────────

def save_supplier(supplier_data: dict) -> int:
    """
    Saves a supplier dictionary to the database.

    Lists (certifications, risk_flags) and dicts (risk_data, logistics_data,
    landed_cost_data) are serialised to JSON strings because SQLite stores
    everything as text or numbers.

    Returns the auto-generated row ID.
    """
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Serialise complex fields to JSON strings
    certs_json    = json.dumps(supplier_data.get("certifications", []))
    flags_json    = json.dumps(supplier_data.get("risk_flags", []))
    risk_json     = json.dumps(supplier_data.get("risk_assessment", {}))
    logistics_json = json.dumps(supplier_data.get("logistics_options", {}))
    landed_json   = json.dumps(supplier_data.get("landed_cost", {}))

    # Pull risk level from nested risk_assessment dict
    risk_assessment = supplier_data.get("risk_assessment", {})
    risk_score = int(risk_assessment.get("overall_risk_score", 0))
    risk_level = risk_assessment.get("risk_level", "Unknown")

    cursor.execute("""
        INSERT INTO suppliers
            (name, website, location, contact_info, product, product_match,
             supplier_type, summary, strengths,
             score, certifications, moq, lead_time, risk_flags, qsr_category,
             supplier_class, origin_country, risk_score, risk_level,
             risk_data, logistics_data, landed_cost_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        supplier_data.get("name", "Unknown"),
        supplier_data.get("website", ""),
        supplier_data.get("location", "Not specified"),
        supplier_data.get("contact_info", "Visit website"),
        supplier_data.get("product", ""),
        # product_match kept for backward compat with old saved rows
        supplier_data.get("product_match", _score_to_match(supplier_data.get("score", 0))),
        supplier_data.get("supplier_type", "Secondary"),
        supplier_data.get("summary", ""),
        supplier_data.get("strengths", ""),
        int(supplier_data.get("score", 0)),
        certs_json,
        supplier_data.get("moq", "Not specified"),
        supplier_data.get("lead_time", "Not specified"),
        flags_json,
        supplier_data.get("qsr_category", "General"),
        supplier_data.get("supplier_class", "Distributor"),
        supplier_data.get("origin_country", "Unknown"),
        risk_score,
        risk_level,
        risk_json,
        logistics_json,
        landed_json,
    ))

    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def _score_to_match(score: int) -> str:
    """Maps a numeric score to the legacy High/Medium/Low label (backward compat)."""
    if score >= 75:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"


def get_all_suppliers() -> pd.DataFrame:
    """
    Fetches all saved suppliers as a Pandas DataFrame, newest first.
    All columns are included — new columns added by migrate_db() appear automatically.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM suppliers ORDER BY saved_at DESC", conn)
    conn.close()
    return df


def delete_supplier(supplier_id: int):
    """Deletes a supplier and their associated scorecard from the database."""
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scorecards WHERE supplier_id = ?", (supplier_id,))
    cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
    conn.commit()
    conn.close()


def supplier_already_saved(name: str, product: str) -> bool:
    """Returns True if a supplier with this name + product is already saved."""
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM suppliers WHERE name = ? AND product = ?",
        (name, product),
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


# ─────────────────────────────────────────────────────────────────────────────
# SCORECARDS
# ─────────────────────────────────────────────────────────────────────────────

def save_scorecard(
    supplier_id: int,
    price: int,
    lead_time: int,
    reliability: int,
    notes: str,
):
    """
    Saves or updates a manual procurement scorecard for a supplier.
    Upserts: if a scorecard exists it is updated; otherwise a new one is inserted.
    """
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM scorecards WHERE supplier_id = ?", (supplier_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE scorecards
            SET price_score=?, lead_time_score=?, reliability_score=?, notes=?, rated_at=?
            WHERE supplier_id=?
        """, (price, lead_time, reliability, notes, datetime.now(), supplier_id))
    else:
        cursor.execute("""
            INSERT INTO scorecards (supplier_id, price_score, lead_time_score, reliability_score, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (supplier_id, price, lead_time, reliability, notes))

    conn.commit()
    conn.close()


def get_scorecard_for_supplier(supplier_id: int) -> dict | None:
    """Returns the existing scorecard for a supplier, or None if not yet rated."""
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT price_score, lead_time_score, reliability_score, notes "
        "FROM scorecards WHERE supplier_id = ?",
        (supplier_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "price_score":       row[0],
            "lead_time_score":   row[1],
            "reliability_score": row[2],
            "notes":             row[3],
        }
    return None


def get_all_scorecards() -> pd.DataFrame:
    """
    Returns all scorecards joined with supplier info for the comparison table.
    Includes new fields: supplier_class, risk_level, landed_cost_data.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT
            s.id               AS supplier_id,
            s.name             AS "Supplier",
            s.product          AS "Product",
            s.location         AS "Location",
            s.supplier_class   AS "Type",
            s.risk_level       AS "Risk Level",
            s.landed_cost_data AS landed_cost_data,
            sc.price_score         AS "Price (1-10)",
            sc.lead_time_score     AS "Lead Time (1-10)",
            sc.reliability_score   AS "Reliability (1-10)",
            ROUND((sc.price_score + sc.lead_time_score + sc.reliability_score) / 3.0, 1)
                               AS "Avg Score",
            sc.notes           AS "Notes",
            sc.rated_at        AS "Last Rated"
        FROM scorecards sc
        JOIN suppliers s ON sc.supplier_id = s.id
        ORDER BY "Avg Score" DESC
    """, conn)
    conn.close()
    return df


# ─────────────────────────────────────────────────────────────────────────────
# JSON HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def parse_json_list(value) -> list:
    """
    Safely parses a JSON string back into a Python list.
    Returns an empty list for None, empty, or malformed values.

    Example:
        parse_json_list('["HACCP", "ISO 22000"]') → ["HACCP", "ISO 22000"]
        parse_json_list(None)                      → []
    """
    if not value:
        return []
    try:
        result = json.loads(value)
        return result if isinstance(result, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def parse_json_dict(value) -> dict:
    """
    Safely parses a JSON string back into a Python dict.
    Returns an empty dict for None, empty, or malformed values.
    """
    if not value:
        return {}
    try:
        result = json.loads(value)
        return result if isinstance(result, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}
