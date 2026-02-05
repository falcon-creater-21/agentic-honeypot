from llm import generate_llm_reply
def agent_reply(stage: int, last_message: str, history: list, intelligence: dict) -> dict:
    """
    Human-like naive victim agent.
    Loop-safe, bank-agnostic, terminal-aware.
    """

    msg = last_message.lower()

    # ---------------- HISTORY ANALYSIS ---------------- #

    otp_mentions = sum(
        1 for h in history
        if isinstance(h, dict) and "otp" in h.get("text", "").lower()
    )

    refusal_made = any(
        isinstance(h, dict)
        and "otp" in h.get("text", "").lower()
        and "safe" in h.get("text", "").lower()
        for h in history
    )

    verification_questions = sum(
        1 for h in history
        if isinstance(h, dict)
        and "verify" in h.get("text", "").lower()
    )

    # ---------------- HARD TERMINAL STATE ---------------- #
    # Once refusal is made → NEVER ask again

    if refusal_made:
        return {
            "reply": "I’m not comfortable sharing sensitive details. I’ll handle this directly with my bank.",
            "note": "Terminal disengagement"
        }

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

    if "account" in msg and stage == 2:
        return {
            "reply": "I have more than one account. Which one are you referring to?",
            "note": "Account clarification"
        }

    if "account" in msg and stage == 3:
        return {
            "reply": "I’m opening my banking app now. Please stay with me.",
            "note": "Delayed compliance"
        }

    if "account" in msg and stage >= 4:
        return {
            "reply": "I can see a long number here, but I want to be sure this is legitimate.",
            "note": "Legitimacy check"
        }

    # ---------------- OTP ESCALATION (STRICT) ---------------- #

    if "otp" in msg and otp_mentions == 1:
        return {
            "reply": "I just received an OTP message. It clearly says not to share it with anyone.",
            "note": "OTP hesitation"
        }

    if "otp" in msg and otp_mentions == 2:
        return {
            "reply": "I’m uncomfortable sharing OTPs. Is there another way to verify?",
            "note": "OTP resistance"
        }

    if "otp" in msg and otp_mentions >= 3:
        return {
            "reply": "I don’t think sharing OTPs is safe. I’ll visit my bank branch instead.",
            "note": "OTP refusal"
        }

    # ---------------- PHISHING / PHONE ---------------- #

    if any(k in msg for k in ["call", "phone", "number", "+91"]):
        return {
            "reply": "I’d rather contact my bank using the number on their official website.",
            "note": "Phone scam avoidance"
        }

    # ---------------- FALLBACKS ---------------- #

    if stage <= 2:
        return {
            "reply": "I’m confused. Can you explain what went wrong?",
            "note": "Early engagement"
        }

    if stage <= 4:
        return {
            "reply": "Please give me a moment. I don’t want to make a mistake.",
            "note": "Delay tactic"
        }

   # ---------- LLM FALLBACK ----------

    llm_reply = generate_llm_reply(history, last_message)

    return {
        "reply": llm_reply,
        "note": "LLM fallback engagement"
    }