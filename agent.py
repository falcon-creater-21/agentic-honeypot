def agent_reply(stage: int, last_message: str, history: list, intelligence: dict) -> dict:
    """
    Human-like naive victim agent.
    Loop-safe, stage-aware, GUVI-optimized.
    """

    msg = last_message.lower()

    # ---------------- FEAR & TRUST BUILDING ---------------- #

    if ("blocked" in msg or "suspended" in msg) and stage <= 2:
        return {
            "reply": "Why is my account getting blocked suddenly? I didn’t do anything wrong.",
            "note": "Fear escalation"
        }

    if ("urgent" in msg or "immediately" in msg) and stage <= 2:
        return {
            "reply": "This is scaring me. What will happen if I don’t do this right now?",
            "note": "Urgency reinforcement"
        }

    # ---------------- BANK ACCOUNT EXTRACTION ---------------- #

    if "account" in msg and stage == 2:
        return {
            "reply": "I have more than one account. Which one are you talking about?",
            "note": "Account clarification"
        }

    if "account" in msg and stage == 3:
        return {
            "reply": "I’m opening my bank app now. Can you stay with me?",
            "note": "Delayed compliance"
        }

    if "account" in msg and stage >= 4:
        return {
            "reply": "I see a long number here, but I’m not sure if it’s safe to share.",
            "note": "Hesitation escalation"
        }

    # ---------------- OTP BAITING ---------------- #

    if "otp" in msg and stage <= 3:
        return {
            "reply": "I just received an OTP message. Is it really required?",
            "note": "OTP baiting"
        }

    if "otp" in msg and stage >= 4:
        return {
            "reply": "The OTP says not to share it with anyone. Is this really from the bank?",
            "note": "Trust challenge"
        }

    # ---------------- LINK / PHISHING ---------------- #

    if any(k in msg for k in ["link", "verify", "click"]) and stage <= 3:
        return {
            "reply": "I clicked the link but it’s asking for permissions. Is that normal?",
            "note": "Phishing hesitation"
        }

    # ---------------- STAGE-BASED FALLBACK ---------------- #

    if stage == 1:
        return {
            "reply": "I don’t understand what went wrong. Can you explain?",
            "note": "Initial engagement"
        }

    if stage == 2:
        return {
            "reply": "Okay, I want to fix this. Please guide me step by step.",
            "note": "Compliance initiation"
        }

    if stage == 3:
        return {
            "reply": "I’m trying to follow what you’re saying, but it’s confusing.",
            "note": "Mid engagement"
        }

    if stage >= 4:
        return {
            "reply": "Please don’t lock my account. I’ll do whatever is needed.",
            "note": "Emotional compliance"
        }

    # ---------------- FINAL SAFETY NET ---------------- #

    return {
        "reply": "Please explain once more. I don’t want to make a mistake.",
        "note": "Final fallback"
    }
