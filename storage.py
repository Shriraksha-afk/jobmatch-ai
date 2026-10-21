import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).parent / "jobmatch_history.db"

def _connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    with _connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                job_title TEXT,
                company TEXT,
                score INTEGER NOT NULL,
                matched_skills TEXT,
                missing_skills TEXT
            )
        """)

def save_analysis(job_title, company, score, matched_skills, missing_skills):
    with _connect() as con:
        con.execute(
            "INSERT INTO analyses (job_title, company, score, matched_skills, missing_skills) VALUES (?, ?, ?, ?, ?)",
            (job_title, company, int(score), ", ".join(matched_skills), ", ".join(missing_skills))
        )

def get_history():
    with _connect() as con:
        return pd.read_sql_query(
            "SELECT created_at AS Date, job_title AS 'Job Title', company AS Company, score AS 'Match Score', matched_skills AS 'Matched Skills', missing_skills AS 'Potential Gaps' FROM analyses ORDER BY id DESC",
            con
        )

def delete_history():
    with _connect() as con:
        con.execute("DELETE FROM analyses")
