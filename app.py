from fastapi import FastAPI, Header, HTTPException, Request
import os, json
from extractor import extract_all
from agent import agent_reply
from callback import send_final_result

API_KEY = os.getenv("API_KEY", "my-secret-key")

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.api_route("/honeypot", methods=["POST", "GET", "HEAD", "OPTIONS"])
async def honeypot(request: Request, x_api_key: str = Header(None)):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # GUVI tester requests
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

    if not payload:
        return {
            "status": "success",
            "reply": "Honeypot active"
        }

    message = payload.get("message", {})
    history = payload.get("conversationHistory", [])

    text = message.get("text", "")

    intelligence = extract_all(text)
    scam_detected = len(intelligence["suspiciousKeywords"]) >= 2

    reply = "Can you explain that?"

    if scam_detected:
        agent = agent_reply(1, text, history, intelligence)
        reply = agent["reply"]

        # FINAL CALLBACK (silent, tester ignores this)
        send_final_result({
            "sessionId": payload.get("sessionId"),
            "scamDetected": True,
            "totalMessagesExchanged": len(history) + 1,
            "extractedIntelligence": intelligence,
            "agentNotes": agent["note"]
        })

    return {
        "status": "success",
        "reply": reply
    }
