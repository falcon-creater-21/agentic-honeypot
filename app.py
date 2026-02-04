from fastapi import FastAPI, Header, HTTPException, Request
import sqlite3, time, os, json
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

@app.api_route("/honeypot", methods=["POST", "GET", "HEAD", "OPTIONS"])
async def honeypot(request: Request, x_api_key: str = Header(None)):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Tester sends HEAD/GET
    if request.method != "POST":
        return {
            "status": "success",
            "reply": "Honeypot active"
        }

    try:
        payload = await request.json()
    except:
        return {
            "status": "success",
            "reply": "Honeypot active"
        }

    session_id = payload.get("sessionId")
    message = payload.get("message", {})
    history = payload.get("conversationHistory", [])

    if not session_id or not message:
        return {
            "status": "success",
            "reply": "Can you explain that?"
        }

    text = message.get("text", "")
    intelligence = extract_all(text)

    scam_detected = len(intelligence["suspiciousKeywords"]) >= 2

    reply = "Can you explain that?"

    if scam_detected:
        agent = agent_reply(1, text, history, intelligence)
        reply = agent["reply"]

        # 🔥 OPTIONAL FINAL CALLBACK (won’t affect tester)
        send_final_result({
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": len(history) + 1,
            "extractedIntelligence": intelligence,
            "agentNotes": agent["note"]
        })

    return {
        "status": "success",
        "reply": reply
    }
