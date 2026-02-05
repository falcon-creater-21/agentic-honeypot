from llm import hf_generate
import random

PROBE_RESPONSES = [
    "Why would my account be blocked suddenly?",
    "What transaction are you talking about?",
    "I didn’t receive any notification from my bank.",
    "Can you explain what exactly went wrong?"
]

DELAY_RESPONSES = [
    "I’m checking my banking app now, give me a moment.",
    "I’m trying to understand this, please wait.",
    "I’m not very technical, can you explain slowly?"
]

REFUSAL_RESPONSES = [
    "I’m not comfortable sharing OTPs.",
    "I won’t share sensitive details here.",
    "This doesn’t seem right to me."
]

EXIT_RESPONSES = [
    "I’ll contact my bank directly.",
    "Please stop contacting me.",
    "I’m ending this conversation now."
]

def agent_reply(stage, last_message, history, intelligence, last_agent_reply):
    msg = last_message.lower()

    # 🔍 PROBE (early)
    if stage <= 2:
        reply = random.choice(PROBE_RESPONSES)

    # ⏳ DELAY (extraction window)
    elif stage <= 4:
        reply = random.choice(DELAY_RESPONSES)

    # 🚫 REFUSE (OTP pressure)
    elif "otp" in msg or "pin" in msg:
        reply = random.choice(REFUSAL_RESPONSES)

    # 🔚 EXIT
    else:
        reply = random.choice(EXIT_RESPONSES)

    # 🧠 OPTIONAL LLM POLISH
    prompt = f"""
Rewrite the following message naturally as a scared bank customer.
Do not add new information.
Message:
"{reply}"
"""
    final_reply = hf_generate(prompt)

    if last_agent_reply and final_reply.lower() == last_agent_reply.lower():
        final_reply = random.choice(EXIT_RESPONSES)

    return {"reply": final_reply}
