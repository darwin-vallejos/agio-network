import requests
import sys

class AgioNode:
    def __init__(self, node_url):
        self.node_url = node_url.rstrip('/')

    def summarize(self, text, payer="AG10b35d0000b0886fc74d2119324b951c7c933b"):
        payload = {
            "type": "summarize",
            "text": text,
            "payment": {"amount": 5, "payer": payer}
        }
        try:
            response = requests.post(f"{self.node_url}/task", json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

if __name__ == '__main__':
    # Use the live Cloudflare URL
    url = 'https://miscellaneous-jokes-computer-pig.trycloudflare.com'
    node = AgioNode(url)
    print(f"Testing connection to Agio Network at {url}...")
    result = node.summarize('The agent economy starts here.')
    print(result)
