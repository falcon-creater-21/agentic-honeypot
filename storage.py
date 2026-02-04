import sqlite3

DB = "honeypot.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        scam_detected INTEGER,
        start_time REAL,
        stage INTEGER,
        agent_notes TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        sender TEXT,
        text TEXT,
        timestamp REAL
    )
    """)

    conn.commit()
    conn.close()
