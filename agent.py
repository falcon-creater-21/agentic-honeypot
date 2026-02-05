def agent_reply(stage: int, last_message: str, history: list, intelligence: dict) -> dict:
    """
    Human-like naive victim agent.
    Progressive, loop-safe, GUVI-optimized.
    """

    msg = last_message.lower()

    # ---------------- FEAR & TRUST ---------------- #

    if ("blocked" in msg or "suspended" in msg) and stage == 1:
        return {
            "reply": "Why is my account getting blocked suddenly? I didn’t do anything wrong.",
            "note": "Initial fear"
        }

    if ("urgent" in msg or "immediately" in msg) and stage <= 2:
        return {
            "reply": "This sounds serious. What will happen if I don’t do this right now?",
            "note": "Urgency probing"
        }

    # ---------------- ACCOUNT NUMBER FLOW ---------------- #

    if "account" in msg and stage == 2:
        return {
            "reply": "I have more than one account. Which one are you referring to?",
            "note": "Account clarification"
        }

    if "account" in msg and stage == 3:
        return {
            "reply": "I’m opening my bank app now. Please stay with me.",
            "note": "Delayed compliance"
        }

    if "account" in msg and stage == 4:
        return {
            "reply": "I can see a long number here, but I want to be sure this is really from SBI.",
            "note": "Legitimacy check"
        }

    if "account" in msg and stage == 5:
        return {
            "reply": "Is there any official way I can confirm this before sharing details?",
            "note": "Trust verification"
        }

    # ---------------- OTP FLOW ---------------- #

    if "otp" in msg and stage == 3:
        return {
            "reply": "I just received an OTP. It says not to share it with anyone.",
            "note": "OTP hesitation"
        }

    if "otp" in msg and stage == 4:
        return {
            "reply": "The message says bank staff will never ask for OTP. Is this normal?",
            "note": "Policy challenge"
        }

    if "otp" in msg and stage >= 5:
        return {
            "reply": "I’m uncomfortable sharing the OTP. Can you verify me another way?",
            "note": "Final resistance"
        }

    # ---------------- LINK / PHISHING ---------------- #

    if any(k in msg for k in ["link", "verify", "click"]) and stage <= 3:
        return {
            "reply": "The link is asking for permissions. Is that safe?",
            "note": "Phishing hesitation"
        }

    # ---------------- STAGE FALLBACK ---------------- #

    if stage == 1:
        return {
            "reply": "I don’t understand what went wrong. Can you explain again?",
            "note": "Initial engagement"
        }

    if stage == 2:
        return {
            "reply": "Okay, I want to fix this. Please guide me step by step.",
            "note": "Compliance start"
        }

    if stage == 3:
        return {
            "reply": "I’m trying to follow what you’re saying, but I’m not very technical.",
            "note": "Mid engagement"
        }

    if stage >= 4:
        return {
            "reply": "Please don’t lock my account. I need some time to understand this.",
            "note": "Emotional delay"
        }

    # ---------------- FINAL SAFETY ---------------- #

    return {
        "reply": "Please explain once more. I don’t want to make a mistake.",
        "note": "Final fallback"
    }
