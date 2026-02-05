from llm import hf_generate

def agent_reply(stage: int, last_message: str, history: list, intelligence: dict, last_agent_reply: str | None) -> dict:
    """
    HF-powered, loop-safe, state-aware honeypot agent.
    """

    history_text = "\n".join(
        f"{h.get('sender', 'unknown')}: {h.get('text', '')}"
        for h in history if isinstance(h, dict)
    )

    prompt = f"""
You are a normal Indian bank customer.
You are scared, cautious, and slightly suspicious.
You NEVER reveal OTPs or full account numbers.
You must NOT repeat your previous reply.
Each reply must be different from before.

Previous reply (DO NOT repeat):
"{last_agent_reply or 'None'}"

Conversation so far:
{history_text}

Scammer just said:
"{last_message}"

Rules:
- Ask a different clarifying question each time
- Gradually become more suspicious
- If OTP pressure continues, move toward refusal
- Reply in ONE natural sentence only

User reply:
"""

    reply = hf_generate(prompt)

    # Final guard against repetition
    if last_agent_reply and reply.strip().lower() == last_agent_reply.strip().lower():
        reply = "This doesn’t feel right. I will contact my bank directly."

    return {
        "reply": reply,
        "note": "HF-generated"
    }
