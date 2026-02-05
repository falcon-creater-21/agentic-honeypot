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

@app.get("/")
def health():
    return {"status": "ok"}

@app.api_route("/honeypot", methods=["POST", "HEAD", "OPTIONS"])
async def honeypot(request: Request, x_api_key: str = Header(None)):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if request.method in ["HEAD", "OPTIONS"]:
        return {"status": "success"}

    try:
        payload = await request.json()
    except Exception:
        return {"status": "success", "reply": "Honeypot active"}

    if not isinstance(payload, dict):
        return {"status": "success", "reply": "Honeypot active"}

    session_id = payload.get("sessionId")
    message = payload.get("message", {})
    history = payload.get("conversationHistory", [])

    if not session_id or not isinstance(message, dict):
        return {"status": "success", "reply": "Honeypot active"}

    text = message.get("text", "")
    sender = message.get("sender", "")
    timestamp = message.get("timestamp", int(time.time() * 1000))

    if not text:
        return {"status": "success", "reply": "Honeypot active"}

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT stage, agent_notes FROM sessions WHERE session_id=?", (session_id,))
    row = cur.fetchone()

    if not row:
        stage = 1
        callback_sent = ""
        cur.execute(
            "INSERT INTO sessions VALUES (?,?,?,?,?)",
            (session_id, 0, time.time(), stage, "")
        )
    else:
        stage, callback_sent = row

    cur.execute(
        "INSERT INTO messages (session_id, sender, text, timestamp) VALUES (?,?,?,?)",
        (session_id, sender, text, timestamp)
    )

    history_texts = [h.get("text", "") for h in history if isinstance(h, dict)]
    full_text = " ".join(history_texts + [text])

    intelligence = extract_all(full_text)

    scam_detected = (
        len(intelligence["suspiciousKeywords"]) >= 2
        or intelligence["bankAccounts"]
        or intelligence["upiIds"]
        or intelligence["phishingLinks"]
    )

    reply_text = "Can you explain that?"

    if scam_detected:
        agent = agent_reply(stage, text, history, intelligence)
        reply_text = agent["reply"]

        cur.execute(
            "UPDATE sessions SET stage=stage+1, scam_detected=1 WHERE session_id=?",
            (session_id,)
        )

    conn.commit()

    # ---------- FINAL CALLBACK (ONCE ONLY) ----------
    should_callback = (
        scam_detected
        and stage >= 4
        and callback_sent == ""
        and (
            intelligence["bankAccounts"]
            or intelligence["upiIds"]
            or intelligence["phishingLinks"]
        )
    )

    if should_callback:
        total_messages = len(history) + 1

        agent_notes = []
        if intelligence["bankAccounts"]:
            agent_notes.append("bank account harvesting")
        if intelligence["upiIds"]:
            agent_notes.append("UPI payment redirection")
        if intelligence["phishingLinks"]:
            agent_notes.append("phishing link delivery")
        if intelligence["suspiciousKeywords"]:
            agent_notes.append("urgency and fear tactics")

        final_payload = {
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": total_messages,
            "extractedIntelligence": intelligence,
            "agentNotes": ", ".join(agent_notes)
        }

        try:
            send_final_result(final_payload)
            cur.execute(
                "UPDATE sessions SET agent_notes=? WHERE session_id=?",
                ("callback_sent", session_id)
            )
            conn.commit()
        except Exception:
            pass

    conn.close()

    return {
        "status": "success",
        "reply": reply_text
    }
