from llm import hf_generate
from intent import detect_intent

def agent_reply(
    stage: int,
    last_message: str,
    history: list,
    intelligence: dict,
    last_agent_reply: str | None,
    phase: str
) -> dict:
    """
    HF-powered, loop-safe, state-aware honeypot agent.
    """

    intent = detect_intent(last_message)

    # TERMINAL EXIT STATE
    if phase == "EXITED":
        return {
            "reply": "I will handle this directly with my bank.",
            "phase": "EXITED"
        }

    # PHASE TRANSITION
    if intent == "OTP":
        next_phase = "RESISTING"
    elif phase == "CONFUSED":
        next_phase = "VERIFYING"
    else:
        next_phase = phase

    history_text = "\n".join(
        f"{h.get('sender','')}: {h.get('text','')}"
        for h in history if isinstance(h, dict)
    )

    prompt = f"""
You are a real Indian bank customer.
You are cautious and suspicious.
You NEVER share OTPs or account numbers.
You NEVER repeat your previous reply.

Current phase: {phase}
Scammer intent: {intent}

Previous reply (DO NOT repeat):
{last_agent_reply or "None"}

Conversation so far:
{history_text}

Scammer just said:
{last_message}

Reply as USER in ONE natural sentence:
"""

    reply = hf_generate(prompt)

    # FINAL LOOP GUARD
    if last_agent_reply and reply.strip().lower() == last_agent_reply.strip().lower():
        reply = "This feels unsafe. I will contact my bank directly."
        next_phase = "EXITED"

    return {
        "reply": reply,
        "phase": next_phase
    }
