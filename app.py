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

# ---------------- HEALTH ---------------- #
@app.get("/")
def health():
    return {"status": "success", "reply": "Honeypot active"}

# ---------------- HONEYPOT ---------------- #
@app.api_route("/honeypot", methods=["POST", "HEAD", "OPTIONS"])
async def honeypot(request: Request, x_api_key: str = Header(None)):

    # AUTH (always JSON)
    if x_api_key != API_KEY:
        return {"status": "error", "reply": "Unauthorized"}

    # Preflight / empty tester calls
    if request.method in ["HEAD", "OPTIONS"]:
        return {"status": "success", "reply": "Honeypot active"}

    # Safe JSON parse
    try:
        payload = await request.json()
    except Exception:
        return {"status": "success", "reply": "Honeypot active"}

    if not isinstance(payload, dict):
        return {"status": "success", "reply": "Honeypot active"}

    session_id = payload.get("sessionId")
    message = payload.get("message")
    history = payload.get("conversationHistory", [])

    if not session_id or not isinstance(message, dict):
        return {"status": "success", "reply": "Honeypot active"}

    text = message.get("text", "")
    if not text:
        return {"status": "success", "reply": "Honeypot active"}

    # ---------------- DB ---------------- #
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT stage, agent_notes, phase FROM sessions WHERE session_id=?",
        (session_id,)
    )
    row = cur.fetchone()

    if not row:
        stage = 1
        last_reply = None
        phase = "CONFUSED"
        cur.execute(
            "INSERT INTO sessions VALUES (?,?,?,?,?,?)",
            (session_id, 0, time.time(), stage, "", phase)
        )
    else:
        stage, last_reply, phase = row

    cur.execute(
        "INSERT INTO messages VALUES (NULL,?,?,?,?)",
        (
            session_id,
            message.get("sender", ""),
            text,
            message.get("timestamp", int(time.time() * 1000))
        )
    )

    # ---------------- INTELLIGENCE ---------------- #
    history_texts = [h.get("text", "") for h in history if isinstance(h, dict)]
    full_text = " ".join(history_texts + [text])
    intelligence = extract_all(full_text)

    scam_detected = len(intelligence["suspiciousKeywords"]) >= 2

    reply_text = "Can you explain that?"

    if scam_detected:
        agent = agent_reply(
            stage=stage,
            last_message=text,
            history=history,
            intelligence=intelligence,
            last_agent_reply=last_reply,
            
        )
        reply_text = agent["reply"]
        new_phase = agent["phase"]

        cur.execute(
            "UPDATE sessions SET stage=stage+1, scam_detected=1, agent_notes=?, phase=? WHERE session_id=?",
            (reply_text, new_phase, session_id)
        )

    conn.commit()
    conn.close()

    # ---------------- FINAL CALLBACK ---------------- #
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

    # EXACT FORMAT GUVI EXPECTS
    return {
        "status": "success",
        "reply": reply_text
    }
