def agent_reply(stage: int, last_message: str, history: list, intelligence: dict) -> dict:
    """
    Rule-guided autonomous agent.
    Adapts to scammer input and extraction progress.
    """

    msg = last_message.lower()

    # ---------- PRIORITY EXTRACTION ----------
    if not intelligence.get("upiIds") and "upi" in msg:
        return {
            "reply": "That UPI didn’t go through. Can you send it again carefully?",
            "note": "UPI clarification"
        }

    if not intelligence.get("bankAccounts") and any(k in msg for k in ["account", "bank"]):
        return {
            "reply": "Can you share the full account number and IFSC? I don’t want any mistake.",
            "note": "Bank detail extraction"
        }

    if not intelligence.get("phishingLinks") and any(k in msg for k in ["link", "click", "verify"]):
        return {
            "reply": "The link isn’t opening on my phone. Can you resend it?",
            "note": "Phishing link extraction"
        }

    # ---------- BEHAVIORAL PROGRESSION ----------
    if "urgent" in msg or "immediately" in msg:
        return {
            "reply": "Why is it so urgent? What exactly will happen?",
            "note": "Urgency probing"
        }

    if "blocked" in msg or "suspended" in msg:
        return {
            "reply": "I don’t understand why it would be blocked. What did I do?",
            "note": "Fear clarification"
        }

    if "send" in msg or "pay" in msg:
        return {
            "reply": "I’ve never done this before. How exactly should I send it?",
            "note": "Payment flow probing"
        }

    # ---------- STAGE FALLBACK ----------
    if stage <= 2:
        return {
            "reply": "Can you explain that once more? I’m confused.",
            "note": "Early engagement"
        }

    if stage <= 4:
        return {
            "reply": "I want to resolve this today. What should I do next?",
            "note": "Mid engagement"
        }

    return {
        "reply": "Please give me the exact steps again. I don’t want any error.",
        "note": "Extended engagement"
    }
