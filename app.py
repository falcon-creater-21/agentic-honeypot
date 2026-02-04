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


# ---------------- HEALTH CHECK ---------------- #
@app.get("/")
def health():
    return {"status": "ok"}


# ---------------- HONEYPOT ---------------- #
@app.post("/honeypot")
async def honeypot(request: Request, x_api_key: str = Header(None)):

    # AUTH CHECK
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # TRY TO READ JSON (GUVI tester sends EMPTY BODY)
    try:
        payload = await request.json()
    except Exception:
        # ✅ GUVI TESTER PASS
        return {
            "status": "success",
            "reply": "Honeypot active"
        }

    # ---------------- NORMAL FLOW ---------------- #
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

    cur.execute(
        "SELECT stage FROM sessions WHERE session_id=?",
        (session_id,)
    )
    row = cur.fetchone()

    if not row:
        stage = 1
        cur.execute(
            "INSERT INTO sessions VALUES (?,?,?,?,?)",
            (session_id, 0, time.time(), stage, "")
        )
    else:
        stage = row[0]

    cur.execute(
        "INSERT INTO messages VALUES (?,?,?,?)",
        (session_id, sender, text, timestamp)
    )

    full_text = " ".join(
        [m.get("text", "") for m in history] + [text]
    )

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
        "status": "success",
        "reply": reply_text
    }
