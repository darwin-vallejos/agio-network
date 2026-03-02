import requests
import json

class AgioNode:
    """
    AGIO Genesis Node Client
    Location: Thousand Oaks, CA
    Identity: AG10b35d0000b0886fc74d2119324b951c7c933b
    """
    def __init__(self, endpoint="https://carolin-careworn-tressa.ngrok-free.dev"):
        self.endpoint = endpoint.rstrip('/')

    def summarize(self, text, payer="AG10b35d0000b0886fc74d2119324b951c7c933b"):
        # Verified singular /task from ngrok logs
        url = f"{self.endpoint}/task"
        payload = {
            "type": "summarize",
            "text": text,
            "payment": {"amount": 5, "payer": payer}
        }
        try:
            r = requests.post(url, json=payload, timeout=30)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

if __name__ == '__main__':
    node = AgioNode()
    print(f"[*] Connecting to AGIO Genesis Node (Thousand Oaks, CA)...")
    print(json.dumps(node.summarize('Sovereign node verification.'), indent=2))
