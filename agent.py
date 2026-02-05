def agent_reply(stage: int, last_message: str, history: list, intelligence: dict) -> dict:
    """
    Human-like naive victim agent.
    Optimized for GUVI evaluation scoring.
    """

    msg = last_message.lower()

    # ---------- EMOTIONAL TRUST FIRST ----------

    if "blocked" in msg or "suspended" in msg:
        return {
            "reply": "Why is my account getting blocked suddenly? I didn’t do anything wrong.",
            "note": "Fear escalation"
        }

    if "urgent" in msg or "immediately" in msg:
        return {
            "reply": "Please don’t block my account. What will happen if I don’t do this now?",
            "note": "Urgency reinforcement"
        }

    # ---------- INTELLIGENCE EXTRACTION ----------

    if "account" in msg and not intelligence["bankAccounts"]:
        return {
            "reply": "Which account number do you need exactly? Please guide me carefully.",
            "note": "Bank account extraction"
        }

    if "ifsc" in msg and not intelligence["bankAccounts"]:
        return {
            "reply": "I’m not sure where to find the IFSC. Can you explain?",
            "note": "IFSC clarification"
        }

    if "upi" in msg and not intelligence["upiIds"]:
        return {
            "reply": "I tried sharing my UPI earlier but it didn’t work. Can you resend yours?",
            "note": "UPI extraction"
        }

    if any(k in msg for k in ["link", "verify", "click"]) and not intelligence["phishingLinks"]:
        return {
            "reply": "The link isn’t opening on my phone. Can you send it again?",
            "note": "Phishing link extraction"
        }

    if "otp" in msg:
        return {
            "reply": "I just received an OTP. Should I share it with you?",
            "note": "OTP baiting"
        }

    # ---------- STAGE-BASED FLOW ----------

    if stage == 1:
        return {
            "reply": "I’m confused. Why is my account at risk?",
            "note": "Initial engagement"
        }

    if stage == 2:
        return {
            "reply": "Okay, I want to fix this. Please tell me what to do next.",
            "note": "Compliance initiation"
        }

    if stage == 3:
        return {
            "reply": "I’m trying to follow your steps, but I’m not very technical.",
            "note": "Delayed compliance"
        }

    if stage >= 4:
        return {
            "reply": "I really don’t want to lose my money. Please help me finish this.",
            "note": "Emotional compliance"
        }

    # ---------- FALLBACK ----------

    return {
        "reply": "Please explain again. I don’t want to make a mistake.",
        "note": "Extended engagement"
    }
