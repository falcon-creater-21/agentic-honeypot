import os
import requests

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = "microsoft/phi-2"

def hf_generate(prompt: str) -> str:
    if not HF_API_KEY:
        return "I’m confused. Can you explain what’s happening?"

    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 80,
            "temperature": 0.85,
            "top_p": 0.9,
            "do_sample": True
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and "generated_text" in data[0]:
            text = data[0]["generated_text"]
            return text.replace(prompt, "").strip()

        return "I’m not sure what to do next."

    except Exception:
        return "I’m confused. Can you explain what’s happening?"
