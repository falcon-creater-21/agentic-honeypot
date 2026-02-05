from llm import hf_generate

def agent_reply(stage: int, last_message: str, history: list, intelligence: dict) -> dict:
    """
    HF-powered human-like honeypot agent.
    No hardcoded replies. No loops.
    """

    history_text = "\n".join(
        f"{h['sender']}: {h['text']}"
        for h in history if isinstance(h, dict)
    )

    prompt = f"""
You are a normal bank customer.
You believe this message might be real.
You are scared, confused, and cautious.
You NEVER reveal OTPs or full details.
You ask realistic questions like a human.
You DO NOT repeat yourself.

Conversation so far:
{history_text}

Scammer just said:
{last_message}

Reply as the USER in one natural sentence.
"""

    reply = hf_generate(prompt)

    return {
        "reply": reply,
        "note": "HF-generated response"
    }
