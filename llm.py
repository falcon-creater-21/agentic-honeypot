import os
import requests

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

HF_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

def generate_llm_reply(history: list, last_message: str) -> str:
    """
    Safe fallback LLM generator.
    Only used when rules cannot decide.
    """

    prompt = (
        "You are a confused but cooperative bank customer.\n"
        "Do NOT reveal you know this is a scam.\n"
        "Ask realistic clarification questions.\n\n"
    )

    for h in history[-6:]:
        prompt += f"{h.get('sender', 'user')}: {h.get('text', '')}\n"

    prompt += f"scammer: {last_message}\nuser:"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 40,
            "temperature": 0.6,
            "top_p": 0.9,
            "do_sample": True
        }
    }

    try:
        res = requests.post(HF_URL, headers=HEADERS, json=payload, timeout=10)
        data = res.json()

        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].split("user:")[-1].strip()

    except Exception:
        pass

    return "Can you please explain this once again?"
