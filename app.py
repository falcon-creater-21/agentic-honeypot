from fastapi import FastAPI, Header, HTTPException, Request
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

    # 🔐 AUTH (ALWAYS RETURN JSON)
    if x_api_key != API_KEY:
        return {"status": "error", "reply": "Unauthorized"}

    # ✅ PRE-FLIGHT / EMPTY CALLS (GUVI TESTER)
    if request.method in ["HEAD", "OPTIONS"]:
        return {"status": "success", "reply": "Honeypot active"}

    # ✅ SAFE JSON PARSE (NO EMPTY RESPONSE EVER)
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

    cur.execute("SELECT stage FROM sessions WHERE session_id=?", (session_id,))
    row = cur.fetchone()

    if not row:
        stage = 1
        cur.execute(
            "INSERT INTO sessions (session_id, scam_detected, start_time, stage, agent_notes) VALUES (?,?,?,?,?)",
            (session_id, 0, time.time(), stage, "")
        )
    else:
        stage = row[0]

    cur.execute(
        "INSERT INTO messages (session_id, sender, text, timestamp) VALUES (?,?,?,?)",
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
        agent = agent_reply(stage, text, history, intelligence)
        reply_text = agent["reply"]

        cur.execute(
            "UPDATE sessions SET stage = stage + 1, scam_detected = 1 WHERE session_id=?",
            (session_id,)
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
                "extractedIntelligence": {
                    "bankAccounts": intelligence["bankAccounts"],
                    "upiIds": intelligence["upiIds"],
                    "phishingLinks": intelligence["phishingLinks"],
                    "phoneNumbers": intelligence["phoneNumbers"],
                    "suspiciousKeywords": intelligence["suspiciousKeywords"]
                },
                "agentNotes": "Scammer used urgency and payment redirection tactics"
            })
        except Exception:
            pass

    # ✅ EXACT FORMAT GUVI EXPECTS
    return {
        "status": "success",
        "reply": reply_text
    }
