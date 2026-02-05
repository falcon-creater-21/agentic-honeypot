def agent_reply(stage: int, last_message: str, history: list, intelligence: dict) -> dict:
    """
    Human-like naive victim agent.
    Escalates compliance gradually and extracts intelligence.
    """

    msg = last_message.lower()

    # ---------- HIGH PRIORITY EXTRACTION ----------

    if "account" in msg and not intelligence["bankAccounts"]:
        return {
            "reply": "I’m scared. Which account number do you need? Please tell me exactly.",
            "note": "Prompting bank account"
        }

    if "ifsc" in msg and not intelligence["bankAccounts"]:
        return {
            "reply": "I’m not sure where to find IFSC. Can you explain?",
            "note": "IFSC clarification"
        }

    if "upi" in msg and not intelligence["upiIds"]:
        return {
            "reply": "I tried sending my UPI earlier but it failed. Can you check again?",
            "note": "UPI extraction"
        }

    if any(k in msg for k in ["link", "verify", "click"]) and not intelligence["phishingLinks"]:
        return {
            "reply": "I clicked the link but nothing happened. Can you resend it?",
            "note": "Phishing link extraction"
        }

    if "otp" in msg:
        return {
            "reply": "I got an OTP message. Should I share it with you?",
            "note": "OTP baiting"
        }

    # ---------- PSYCHOLOGICAL ENGAGEMENT ----------

    if "urgent" in msg or "immediately" in msg:
        return {
            "reply": "Please don’t block my account. What will happen if I don’t do this now?",
            "note": "Urgency reinforcement"
        }

    if "blocked" in msg or "suspended" in msg:
        return {
            "reply": "Why is my account getting blocked suddenly? I didn’t do anything wrong.",
            "note": "Fear escalation"
        }

    # ---------- STAGE-BASED FLOW ----------

    if stage == 1:
        return {
            "reply": "I’m confused. Why is my account at risk?",
            "note": "Initial engagement"
        }

    if stage == 2:
        return {
            "reply": "Okay, I want to fix this. Please guide me step by step.",
            "note": "Compliance initiation"
        }

    if stage == 3:
        return {
            "reply": "I’m trying to follow your instructions but I’m not very technical.",
            "note": "Delayed compliance"
        }

    if stage == 4:
        return {
            "reply": "I really don’t want to lose my money. Please help me finish this.",
            "note": "Emotional compliance"
        }

    # ---------- FINAL FALLBACK ----------

    return {
        "reply": "Please explain once more. I don’t want to make any mistake.",
        "note": "Extended engagement"
    }
