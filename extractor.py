import re

def extract_all(text: str) -> dict:
    text_lower = text.lower()

    upi_ids = re.findall(
        r'\b[a-zA-Z0-9.\-_]{2,}@(upi|ybl|oksbi|okhdfcbank|okaxis|paytm)\b',
        text_lower
    )

    bank_accounts = re.findall(
        r'\b(account|a/c|acc|bank)\s*[:\-]?\s*(\d{9,18})\b',
        text_lower
    )

    phishing_links = re.findall(
        r'https?://[^\s]+',
        text
    )

    phone_numbers = re.findall(
        r'\+91\d{10}',
        text
    )

    suspicious_keywords_list = [
        "urgent", "immediately", "verify", "blocked",
        "suspended", "freeze", "limited", "warning",
        "action required", "last chance"
    ]

    suspicious_keywords = [
        k for k in suspicious_keywords_list if k in text_lower
    ]

    return {
        "upiIds": list(set(upi_ids)),
        "bankAccounts": list(set(acc for _, acc in bank_accounts)),
        "phishingLinks": list(set(phishing_links)),
        "phoneNumbers": list(set(phone_numbers)),
        "suspiciousKeywords": suspicious_keywords
    }
