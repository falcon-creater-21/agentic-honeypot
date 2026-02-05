import os
import requests

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

def hf_generate(prompt: str) -> str:
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 80,
            "temperature": 0.8,
            "top_p": 0.9,
            "do_sample": True
        }
    }

    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()

    data = response.json()

    return data[0]["generated_text"].replace(prompt, "").strip()
