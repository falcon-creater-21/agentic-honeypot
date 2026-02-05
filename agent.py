def agent_reply(stage: int, last_message: str, history: list, intelligence: dict) -> dict:
    """
    Human-like naive victim agent.
    Stateful, progressive, loop-safe, bank-agnostic.
    """

    msg = last_message.lower()

    # ---------------- HISTORY SIGNALS ---------------- #

    otp_mentions = sum(
        1 for h in history
        if isinstance(h, dict) and "otp" in h.get("text", "").lower()
    )

    account_mentions = sum(
        1 for h in history
        if isinstance(h, dict) and "account" in h.get("text", "").lower()
    )

    # ---------------- INITIAL FEAR ---------------- #

    if ("blocked" in msg or "suspended" in msg) and stage == 1:
        return {
            "reply": "Why is my account getting blocked suddenly? I didn’t do anything wrong.",
            "note": "Initial fear"
        }

    if ("urgent" in msg or "immediately" in msg) and stage <= 2:
        return {
            "reply": "This sounds serious. What exactly will happen if I don’t do this now?",
            "note": "Urgency probing"
        }

    # ---------------- ACCOUNT NUMBER FLOW ---------------- #

    if "account" in msg and account_mentions == 1:
        return {
            "reply": "I have more than one account. Which one are you referring to?",
            "note": "Account clarification"
        }

    if "account" in msg and account_mentions == 2:
        return {
            "reply": "I’m opening my banking app now. Please stay with me.",
            "note": "Delayed compliance"
        }

    if "account" in msg and account_mentions == 3:
        return {
            "reply": "I can see a long number here, but I want to be sure this is legitimate.",
            "note": "Legitimacy check"
        }

    if "account" in msg and account_mentions >= 4:
        return {
            "reply": "Is there any official way I can verify this before sharing details?",
            "note": "Trust verification"
        }

    # ---------------- OTP FLOW (KEY FIX) ---------------- #

    if "otp" in msg and otp_mentions == 1:
        return {
            "reply": "I just received an OTP message. It says not to share it with anyone.",
            "note": "OTP hesitation"
        }

    if "otp" in msg and otp_mentions == 2:
        return {
            "reply": "The message clearly warns not to share OTPs. Why is it required here?",
            "note": "OTP policy challenge"
        }

    if "otp" in msg and otp_mentions == 3:
        return {
            "reply": "I’m really uncomfortable sharing the OTP. Is there another way?",
            "note": "OTP resistance"
        }

    if "otp" in msg and otp_mentions >= 4:
        return {
            "reply": "I don’t think sharing OTPs is safe. I’ll visit my bank branch instead.",
            "note": "Final refusal"
        }

    # ---------------- PHISHING / LINK ---------------- #

    if any(k in msg for k in ["link", "verify", "click"]):
        return {
            "reply": "The link is asking for permissions. Is that normal?",
            "note": "Phishing hesitation"
        }

    # ---------------- STAGE FALLBACK ---------------- #

    if stage == 1:
        return {
            "reply": "I’m confused about what went wrong. Can you explain again?",
            "note": "Initial engagement"
        }

    if stage == 2:
        return {
            "reply": "Okay, I want to fix this. Please tell me what I should do next.",
            "note": "Compliance start"
        }

    if stage == 3:
        return {
            "reply": "I’m trying to follow, but I’m not very technical.",
            "note": "Mid engagement"
        }

    if stage >= 4:
        return {
            "reply": "Please give me some time. I don’t want to make a mistake.",
            "note": "Emotional delay"
        }

    # ---------------- FINAL SAFETY ---------------- #

    return {
        "reply": "Please explain once more. I’m really worried.",
        "note": "Final fallback"
    }
