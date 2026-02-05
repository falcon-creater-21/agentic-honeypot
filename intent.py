def detect_intent(text: str) -> str:
    t = text.lower()
    if "otp" in t:
        return "OTP"
    if "upi" in t:
        return "UPI"
    if "account" in t or "a/c" in t:
        return "ACCOUNT"
    if "+91" in t or "call" in t:
        return "PHONE"
    return "GENERIC"
