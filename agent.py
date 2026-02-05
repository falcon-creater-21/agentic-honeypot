from llm import hf_generate
from intent import detect_intent

def agent_reply(stage, last_message, history, intelligence, last_reply, phase):
    intent = detect_intent(last_message)

    # 🚫 HARD TERMINAL STATE
    if phase == "EXITED":
        return {
            "reply": "I will handle this directly with my bank.",
            "phase": "EXITED"
        }

    # 🔄 PHASE TRANSITIONS
    if intent == "OTP" and phase != "EXITED":
        next_phase = "RESISTING"
    elif phase == "CONFUSED":
        next_phase = "VERIFYING"
    else:
        next_phase = phase

    prompt = f"""
You are a real Indian bank customer.

Current phase: {phase}
Scammer intent: {intent}

Rules:
- NEVER repeat previous replies
- NEVER reveal OTP, UPI, or full account numbers
- Respond ONLY to the scammer's last message
- Move naturally between phases
- ONE sentence only

Previous reply (avoid repeating):
{last_reply or "None"}

Conversation:
{last_message}

Respond as the USER:
"""

    reply = hf_generate(prompt)

    # 🛑 FINAL SAFETY GUARD
    if last_reply and reply.strip().lower() == last_reply.strip().lower():
        reply = "This feels unsafe. I will contact my bank directly."
        next_phase = "EXITED"

    return {
        "reply": reply,
        "phase": next_phase
    }
