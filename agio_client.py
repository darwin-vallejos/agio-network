import requests
import sys
import json

class AgioNode:
    def __init__(self, node_url):
        self.node_url = node_url.rstrip('/')

    def summarize(self, text, payer="AG10b35d0000b0886fc74d2119324b951c7c933b"):
        url = f"{self.node_url}/tasks"
        payload = {
            "type": "summarize",
            "text": text,
            "payment": {"amount": 5, "payer": payer}
        }
        try:
            headers = {'User-Agent': 'AgioNode/2.0', 'Accept': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Gateway Error", "status": response.status_code}
        except Exception as e:
            return {"error": str(e)}

if __name__ == '__main__':
    url = 'https://miscellaneous-jokes-computer-pig.trycloudflare.com'
    node = AgioNode(url)
    print(f"[*] Connecting to AGIO Genesis Node: {url}")
    result = node.summarize('Verify the sovereign agent economy.')
    print(json.dumps(result, indent=2))
