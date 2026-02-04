def agent_reply(stage: int, last_message: str, history: list, intelligence: dict) -> dict:
    """
    Rule-guided autonomous honeypot agent.
    """

    msg = last_message.lower()

    # ---------- EXTRACTION PRIORITY ----------
    if not intelligence.get("upiIds") and "upi" in msg:
        return {
            "reply": "That UPI didn’t work. Can you send it again carefully?",
            "note": "UPI extraction"
        }

    if not intelligence.get("bankAccounts") and any(k in msg for k in ["account", "bank"]):
        return {
            "reply": "Please share the full account number and IFSC. I don’t want any mistake.",
            "note": "Bank extraction"
        }

    if not intelligence.get("phishingLinks") and any(k in msg for k in ["link", "verify", "click"]):
        return {
            "reply": "The link isn’t opening for me. Can you resend it?",
            "note": "Link extraction"
        }

    # ---------- SOCIAL ENGINEERING ----------
    if "urgent" in msg or "immediately" in msg:
        return {
            "reply": "Why is it so urgent? What exactly will happen?",
            "note": "Urgency probing"
        }

    if "blocked" in msg or "suspended" in msg:
        return {
            "reply": "I don’t understand why my account would be blocked. What happened?",
            "note": "Fear probing"
        }

    if "send" in msg or "pay" in msg:
        return {
            "reply": "I’ve never done this before. How exactly should I send it?",
            "note": "Payment probing"
        }

    # ---------- FALLBACK ----------
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
        "reply": "Please give me the exact steps again. I don’t want to make any mistake.",
        "note": "Extended engagement"
    }
