import os
import requests

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = "microsoft/phi-2"

def hf_generate(prompt: str) -> str:
    if not HF_API_KEY:
        return "I’m not sure what’s happening. Can you explain again?"

    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 60,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].replace(prompt, "").strip()

        return "Can you explain what I should do next?"

    except Exception:
        # 🔐 NEVER break honeypot
        return "I’m confused. Can you explain what’s happening?"
