from llm import hf_generate
from intent import detect_intent
import random

EXIT_REPLIES = [
    "I’m not comfortable continuing this conversation.",
    "I’ve decided to contact my bank directly.",
    "I won’t share sensitive information here.",
    "I’m ending this conversation now.",
    "Please stop contacting me. I’ll handle this with my bank."
]

def agent_reply(
    stage: int,
    last_message: str,
    history: list,
    intelligence: dict,
    last_agent_reply: str | None,
    phase: str
) -> dict:

    intent = detect_intent(last_message)

    history_text = "\n".join(
        f"{h.get('sender','')}: {h.get('text','')}"
        for h in history if isinstance(h, dict)
    )

    # 🟥 SAFE DISENGAGEMENT PHASE (NO HARD LOOP)
    if phase == "EXITED":
        reply = random.choice(
            [r for r in EXIT_REPLIES if r != last_agent_reply]
            or EXIT_REPLIES
        )
        return {
            "reply": reply,
            "phase": "EXITED"
        }

    # 🔄 PHASE TRANSITIONS
    if intent == "OTP":
        next_phase = "RESISTING"
    elif phase == "CONFUSED":
        next_phase = "VERIFYING"
    else:
        next_phase = phase

    prompt = f"""
You are a real Indian bank customer.
You are scared but cautious.
You NEVER share OTPs or account numbers.
You must NEVER repeat the same sentence.
You respond naturally to the scammer.

Conversation so far:
{history_text}

Scammer just said:
{last_message}

Reply as USER in ONE natural sentence:
"""

    reply = hf_generate(prompt)

    # 🛡️ FINAL LOOP GUARD
    if last_agent_reply and reply.strip().lower() == last_agent_reply.strip().lower():
        reply = random.choice(EXIT_REPLIES)
        next_phase = "EXITED"

    # 🧠 AUTO EXIT AFTER HEAVY PRESSURE
    if stage >= 5 and intent in ["OTP", "ACCOUNT", "THREAT"]:
        next_phase = "EXITED"

    return {
        "reply": reply,
        "phase": next_phase
    }
