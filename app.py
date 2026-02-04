from fastapi import FastAPI, Header, HTTPException, Request
import sqlite3, time, os

from storage import init_db
from extractor import extract_all
from agent import agent_reply
from callback import send_final_result

API_KEY = os.getenv("API_KEY", "my-secret-key")
DB_PATH = "honeypot.db"
DEBUG_MODE = True

app = FastAPI()
init_db()

# ---------- HEALTH CHECK (MANDATORY) ----------
@app.get("/")
def health():
    return {"status": "ok", "service": "agentic-honeypot"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ---------- MAIN ENDPOINT ----------
@app.post("/honeypot")
async def honeypot(request: Request, x_api_key: str = Header(None)):

    # ---- AUTH ----
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ---- SAFE BODY PARSE ----
    try:
        payload = await request.json()
    except:
        # GUVI tester sends empty body sometimes
        return {
            "status": "success",
            "reply": "Hello. How can I help you?"
        }

    # ---- HANDLE EMPTY BODY ----
    if not payload:
        return {
            "status": "success",
            "reply": "Hello. How can I help you?"
        }

    session_id = payload.get("sessionId")
    message = payload.get("message", {})
    history = payload.get("conversationHistory", [])

    if not session_id or not message:
        return {
            "status": "success",
            "reply": "Can you explain that?"
        }

    sender = message.get("sender", "")
    text = message.get("text", "")
    timestamp = message.get("timestamp", int(time.time() * 1000))

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ---- SESSION INIT ----
    cur.execute(
        "SELECT stage, scam_detected FROM sessions WHERE session_id=?",
        (session_id,)
    )
    row = cur.fetchone()

    if not row:
        stage = 1
        scam_detected = 0
        cur.execute(
            "INSERT INTO sessions VALUES (?,?,?,?,?)",
            (session_id, 0, time.time(), stage, "")
        )
    else:
        stage, scam_detected = row

    # ---- STORE MESSAGE ----
    cur.execute(
        "INSERT INTO messages VALUES (?,?,?,?)",
        (session_id, sender, text, timestamp)
    )

    full_text = " ".join([m.get("text", "") for m in history] + [text])

    intelligence = extract_all(full_text)

    risk_score = len(intelligence["suspiciousKeywords"])
    scam_detected = risk_score >= 2

    reply = "Can you explain that?"

    if scam_detected:
        agent = agent_reply(stage, text, history, intelligence)
        reply = agent["reply"]

        cur.execute(
            "UPDATE sessions SET scam_detected=1, stage=stage+1, agent_notes=? WHERE session_id=?",
            (agent["note"], session_id)
        )

    if DEBUG_MODE:
        print("\n--- AGENT TRACE ---")
        print("SESSION:", session_id)
        print("STAGE:", stage)
        print("SCAM:", scam_detected)
        print("AGENT:", reply)
        print("INTEL:", intelligence)
        print("-------------------\n")

    conn.commit()

    # ---- FINAL CALLBACK ----
    if scam_detected and stage >= 4:
        cur.execute(
            "SELECT COUNT(*) FROM messages WHERE session_id=?",
            (session_id,)
        )
        total_msgs = cur.fetchone()[0]

        send_final_result({
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": total_msgs,
            "extractedIntelligence": intelligence,
            "agentNotes": "Scammer engaged successfully"
        })

        cur.execute(
            "UPDATE sessions SET stage=99 WHERE session_id=?",
            (session_id,)
        )
        conn.commit()

    conn.close()

    return {
        "status": "success",
        "reply": reply
    }
