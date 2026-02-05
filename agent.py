from llm import hf_generate
import random

FALLBACKS = [
    "Why is my account suddenly at risk?",
    "I haven’t received any official message from my bank.",
    "Can you explain what transaction caused this?",
    "This doesn’t seem right to me."
]

EXIT_LINES = [
    "I’ll contact my bank directly.",
    "I’m not comfortable sharing details here.",
    "Please stop contacting me."
]

def agent_reply(stage, last_message, history, intelligence, last_agent_reply):
    msg = last_message.lower()

    # Hard stop on OTP pressure
    if "otp" in msg or "pin" in msg:
        reply = random.choice(EXIT_LINES)

    elif stage <= 2:
        reply = random.choice(FALLBACKS)

    elif stage <= 4:
        reply = "I’m checking my bank app now, please wait."

    else:
        reply = random.choice(EXIT_LINES)

    prompt = f"""
Rewrite this as a scared Indian bank customer.
Do NOT repeat previous reply.
Message:
"{reply}"
"""

    final_reply = hf_generate(prompt)

    if last_agent_reply and final_reply.lower() == last_agent_reply.lower():
        final_reply = random.choice(EXIT_LINES)

    return {"reply": final_reply}
