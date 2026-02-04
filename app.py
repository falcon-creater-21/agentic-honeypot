from fastapi import FastAPI, Header, HTTPException, Request
import sqlite3
import time
import os

from storage import init_db
from extractor import extract_all
from agent import agent_reply
from callback import send_final_result

# ---------------- CONFIG ---------------- #
API_KEY = os.getenv("API_KEY", "my-secret-key")
DB_PATH = "honeypot.db"

# ---------------- APP INIT ---------------- #
app = FastAPI()

# Always re-init DB safely on startup
init_db()


# ---------------- HEALTH CHECK ---------------- #
@app.get("/")
def health():
    return {"status": "ok"}


# ---------------- HONEYPOT ENDPOINT ---------------- #
@app.post("/honeypot")
async def honeypot(request: Request, x_api_key: str = Header(None)):

    # ---------- AUTH ----------
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ---------- GUVI TESTER HANDLING ----------
    # GUVI sends POST with EMPTY body
    try:
        payload = await request.json()
    except Exception:
        return {
            "status": "success",
            "reply": "Honeypot active"
        }

    # ---------- NORMAL FLOW ----------
    session_id = payload.get("sessionId")
    message = payload.get("message", {})
    history = payload.get("conversationHistory", [])

    if not session_id or not message:
        return {
            "status": "success",
            "reply": "Honeypot active"
        }

    sender = message.get("sender", "")
    text = message.get("text", "")
    timestamp = message.get("timestamp", int(time.time() * 1000))

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ---------- SESSION ----------
    cur.execute(
        "SELECT stage FROM sessions WHERE session_id=?",
        (session_id,)
    )
    row = cur.fetchone()

    if not row:
        stage = 1
        cur.execute(
            """
            INSERT INTO sessions (session_id, scam_detected, start_time, stage, agent_notes)
            VALUES (?,?,?,?,?)
            """,
            (session_id, 0, time.time(), stage, "")
        )
    else:
        stage = row[0]

    # ---------- STORE MESSAGE (FIXED) ----------
    cur.execute(
        """
        INSERT INTO messages (session_id, sender, text, timestamp)
        VALUES (?,?,?,?)
        """,
        (session_id, sender, text, timestamp)
    )

    # ---------- ANALYSIS ----------
    full_text = " ".join([m.get("text", "") for m in history] + [text])
    intelligence = extract_all(full_text)

    suspicious = intelligence.get("suspiciousKeywords", [])
    scam_detected = len(suspicious) >= 2

    reply_text = "Can you explain that?"

    # ---------- AGENT ----------
    if scam_detected:
        agent = agent_reply(stage, text, history, intelligence)
        reply_text = agent["reply"]

        cur.execute(
            """
            UPDATE sessions
            SET stage=stage+1, scam_detected=1
            WHERE session_id=?
            """,
            (session_id,)
        )

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "reply": reply_text
    }
