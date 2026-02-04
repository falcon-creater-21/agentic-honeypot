from fastapi import FastAPI, Header, HTTPException
import sqlite3
import time
import os

from storage import init_db
from extractor import extract_all
from agent import agent_reply
from callback import send_final_result

# ---------------- CONFIG ---------------- #

API_KEY = os.getenv("API_KEY", "my-secret-key")
DEBUG_MODE = True
DB_PATH = "honeypot.db"

# ---------------- APP INIT ---------------- #

app = FastAPI()
init_db()

# ---------------- ENDPOINT ---------------- #

@app.post("/honeypot")
def honeypot(payload: dict, x_api_key: str = Header(None)):

    # ---------- AUTH ----------
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ---------- SAFE PARSE ----------
    session_id = payload.get("sessionId")
    message = payload.get("message", {})
    history = payload.get("conversationHistory", [])

    if not session_id or not message:
        return {"status": "success", "reply": "Can you explain that?"}

    sender = message.get("sender", "")
    text = message.get("text", "")
    timestamp = message.get("timestamp", int(time.time() * 1000))

    # ---------- DB CONNECT ----------
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ---------- SESSION INIT ----------
    cur.execute(
        "SELECT stage, scam_detected FROM sessions WHERE session_id=?",
        (session_id,)
    )
    row = cur.fetchone()

    if not row:
        stage = 1
        scam_detected = 0
        cur.execute(
            """
            INSERT INTO sessions (session_id, scam_detected, start_time, stage, agent_notes)
            VALUES (?,?,?,?,?)
            """,
            (session_id, 0, time.time(), stage, "")
        )
    else:
        stage, scam_detected = row

    # ---------- STORE MESSAGE ----------
    cur.execute(
        """
        INSERT INTO messages (session_id, sender, text, timestamp)
        VALUES (?,?,?,?)
        """,
        (session_id, sender, text, timestamp)
    )

    # ---------- FULL TEXT ----------
    full_text = " ".join(
        [m.get("text", "") for m in history] + [text]
    )

    # ---------- INTELLIGENCE ----------
    intelligence = extract_all(full_text)

    suspicious = intelligence.get("suspiciousKeywords", [])

    high_risk_terms = [
        "upi", "account", "send money", "verify",
        "blocked", "urgent", "immediately"
    ]

    risk_score = len(suspicious)
    risk_score += sum(
        1 for t in high_risk_terms if t in full_text.lower()
    )

    scam_detected = risk_score >= 2

    # ---------- AGENT ----------
    agent_reply_text = "Can you explain that?"

    if scam_detected:
        agent = agent_reply(
            stage=stage,
            last_message=text,
            history=history,
            intelligence=intelligence
        )
        agent_reply_text = agent["reply"]

        cur.execute(
            """
            UPDATE sessions
            SET scam_detected=1, stage=stage+1, agent_notes=?
            WHERE session_id=?
            """,
            (agent["note"], session_id)
        )

    # ---------- DEBUG ----------
    if DEBUG_MODE:
        print("\n--- AGENT TRACE ---")
        print("SESSION:", session_id)
        print("STAGE:", stage)
        print("SCAM:", scam_detected)
        print("RISK SCORE:", risk_score)
        print("AGENT:", agent_reply_text)
        print("INTEL:", intelligence)
        print("-------------------\n")

    conn.commit()

    # ---------- FINAL CALLBACK ----------
    if scam_detected and stage >= 4:
        cur.execute(
            "SELECT COUNT(*) FROM messages WHERE session_id=?",
            (session_id,)
        )
        total_msgs = cur.fetchone()[0]

        final_payload = {
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": total_msgs,
            "extractedIntelligence": intelligence,
            "agentNotes": "Scammer engaged and intelligence extracted"
        }

        send_final_result(final_payload)

        # prevent duplicate callbacks
        cur.execute(
            "UPDATE sessions SET stage=99 WHERE session_id=?",
            (session_id,)
        )
        conn.commit()

    conn.close()

    return {
        "status": "success",
        "reply": agent_reply_text
    }
