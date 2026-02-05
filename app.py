from fastapi import FastAPI, Header, Request
import sqlite3, time, os

from storage import init_db
from extractor import extract_all
from agent import agent_reply
from callback import send_final_result

API_KEY = os.getenv("API_KEY", "my-secret-key")
DB_PATH = "honeypot.db"

app = FastAPI()
init_db()

@app.get("/")
def health():
    return {"status": "success", "reply": "Honeypot active"}

@app.api_route("/honeypot", methods=["POST", "HEAD", "OPTIONS"])
async def honeypot(request: Request, x_api_key: str = Header(None)):

    if x_api_key != API_KEY:
        return {"status": "error", "reply": "Unauthorized"}

    if request.method in ["HEAD", "OPTIONS"]:
        return {"status": "success", "reply": "Honeypot active"}

    try:
        payload = await request.json()
    except Exception:
        return {"status": "success", "reply": "Honeypot active"}

    session_id = payload.get("sessionId")
    message = payload.get("message")
    history = payload.get("conversationHistory", [])

    if not session_id or not isinstance(message, dict):
        return {"status": "success", "reply": "Honeypot active"}

    text = message.get("text", "")
    if not text:
        return {"status": "success", "reply": "Honeypot active"}

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT stage, agent_notes FROM sessions WHERE session_id=?", (session_id,))
    row = cur.fetchone()

    if not row:
        stage = 1
        last_agent_reply = None
        cur.execute(
            "INSERT INTO sessions VALUES (?,?,?,?,?)",
            (session_id, 0, time.time(), stage, "")
        )
    else:
        stage, last_agent_reply = row

    cur.execute(
        "INSERT INTO messages VALUES (NULL,?,?,?,?)",
        (
            session_id,
            message.get("sender", ""),
            text,
            message.get("timestamp", int(time.time() * 1000))
        )
    )

    full_text = " ".join(h.get("text", "") for h in history if isinstance(h, dict)) + " " + text
    intelligence = extract_all(full_text)

    scam_detected = len(intelligence["suspiciousKeywords"]) >= 2

    reply_text = "Can you explain that?"

    if scam_detected:
        agent = agent_reply(stage, text, history, intelligence, last_agent_reply)
        reply_text = agent["reply"]

        cur.execute(
            "UPDATE sessions SET stage=stage+1, scam_detected=1, agent_notes=? WHERE session_id=?",
            (reply_text, session_id)
        )

    conn.commit()
    conn.close()

    if scam_detected and stage >= 3:
        try:
            send_final_result({
                "sessionId": session_id,
                "scamDetected": True,
                "totalMessagesExchanged": stage,
                "extractedIntelligence": intelligence,
                "agentNotes": "HF-driven adaptive engagement"
            })
        except Exception:
            pass

    return {
        "status": "success",
        "reply": reply_text
    }
