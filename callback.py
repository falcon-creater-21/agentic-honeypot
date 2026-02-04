import requests

GUVI_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

def send_final_result(payload):
    return requests.post(GUVI_URL, json=payload, timeout=5)
