from fastapi import FastAPI, Header, HTTPException, Request
import sqlite3, time, os, json

from storage import init_db
from extractor import extract_all
from agent import agent_reply

EMPTY_RESPONSE = {
    "scam_detected": False,
    "confidence": 0.0,
    "engagement_metrics": {
        "turns": 0,
        "duration_seconds": 0
    },
    "extracted_intelligence": {
        "upi_ids": [],
        "bank_accounts": [],
        "phishing_urls": []
    }
}

API_KEY = os.getenv("API_KEY", "my-secret-key")
DB_PATH = "honeypot.db"

app = FastAPI()
init_db()

# ---------------- HEALTH ---------------- #
@app.get("/")
def health():
    return {"status": "ok"}

# ---------------- HONEYPOT ---------------- #
@app.api_route("/honeypot", methods=["GET", "POST", "HEAD", "OPTIONS"])
async def honeypot(request: Request, x_api_key: str = Header(None)):

    # AUTH
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # GUVI GET / HEAD / OPTIONS
    if request.method in ["GET", "HEAD", "OPTIONS"]:
        return {
            "status": "success",
            "reply": "Honeypot active"
        }

    # SAFE BODY PARSE
    try:
        body = await request.body()
        payload = json.loads(body) if body else {}
    except Exception:
        payload = {}

    # EMPTY BODY (GUVI POST)
    if not payload:
        return {
            "status": "success",
            "reply": "Honeypot active"
        }

    # ---------------- NORMAL FLOW ---------------- #
    session_id = payload.get("sessionId")
    message = payload.get("message", {})
    history = payload.get("conversationHistory", [])

    if not session_id or not message:
        return EMPTY_RESPONSE


    sender = message.get("sender", "")
    text = message.get("text", "")
    timestamp = message.get("timestamp", int(time.time() * 1000))

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
        (session_id, sender, text, timestamp)
    )

    full_text = " ".join([m.get("text", "") for m in history] + [text])
    intelligence = extract_all(full_text)

    scam_detected = len(intelligence.get("suspiciousKeywords", [])) >= 2

    reply_text = "Can you explain that?"

    if scam_detected:
        agent = agent_reply(stage, text, history, intelligence)
        reply_text = agent["reply"]

        cur.execute(
            "UPDATE sessions SET stage=stage+1, scam_detected=1 WHERE session_id=?",
            (session_id,)
        )

    conn.commit()
    conn.close()

    return {
    "scam_detected": scam_detected,
    "confidence": 0.85 if scam_detected else 0.1,
    "engagement_metrics": {
        "turns": stage,
        "duration_seconds": 10
    },
    "extracted_intelligence": {
        "upi_ids": intelligence["upiIds"],
        "bank_accounts": intelligence["bankAccounts"],
        "phishing_urls": intelligence["phishingLinks"]
    }
}

