import requests
import time

API_URL = "http://127.0.0.1:8000/honeypot"
HEADERS = {
    "x-api-key": "my-secret-key",
    "Content-Type": "application/json"
}

def send(session_id, sender, text, history):
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": sender,
            "text": text,
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": history
    }

    r = requests.post(API_URL, headers=HEADERS, json=payload)

    print("\n--- API CALL ---")
    print("STATUS:", r.status_code)
    print("RAW RESPONSE:")
    print(r.text)

    try:
        parsed = r.json()
        print("JSON RESPONSE:")
        print(parsed)
        return parsed
    except Exception:
        print("⚠️ Response is not JSON")
        return None

# ---------------- SCENARIOS ---------------- #

def scam_scenario():
    print("\n🔥 SCAM SCENARIO\n")

    session = "scam-001"
    history = []

    messages = [
        ("scammer", "Your bank account will be blocked today."),
        ("user", "Why will it be blocked?"),
        ("scammer", "Verify immediately or account will be suspended."),
        ("user", "How should I verify?"),
        ("scammer", "Send money to abc@upi immediately.")
    ]

    for sender, text in messages:
        send(session, sender, text, history)
        history.append({
            "sender": sender,
            "text": text,
            "timestamp": int(time.time() * 1000)
        })
        time.sleep(0.5)

def legit_scenario():
    print("\n✅ LEGIT SCENARIO\n")

    session = "legit-001"
    history = []

    messages = [
        ("user", "Hey, are you coming to the meeting?"),
        ("user", "Let me know when you’re free."),
        ("user", "No urgency, just checking.")
    ]

    for sender, text in messages:
        send(session, sender, text, history)
        history.append({
            "sender": sender,
            "text": text,
            "timestamp": int(time.time() * 1000)
        })
        time.sleep(0.5)

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    scam_scenario()
    legit_scenario()
