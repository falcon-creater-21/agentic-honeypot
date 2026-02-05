import sqlite3

DB_PATH = "honeypot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    scam_detected INTEGER,
    start_time REAL,
    stage INTEGER,
    agent_notes TEXT,
    phase TEXT
)
""")


    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        sender TEXT,
        text TEXT,
        timestamp INTEGER
    )
    """)

    conn.commit()
    conn.close()
