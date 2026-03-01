import requests
import sys

class AgioNode:
    def __init__(self, node_url):
        self.node_url = node_url.rstrip('/')

    def summarize(self, text, payer="AG10b35d0000b0886fc74d2119324b951c7c933b"):
        # Ensure we use /tasks (plural) as seen in your logs
        url = f"{self.node_url}/tasks"
        payload = {
            "type": "summarize",
            "text": text,
            "payment": {"amount": 5, "payer": payer}
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": response.status_code, "raw": response.text[:100]}
        except Exception as e:
            return {"error": str(e)}

if __name__ == '__main__':
    url = 'https://miscellaneous-jokes-computer-pig.trycloudflare.com'
    node = AgioNode(url)
    print(f"Testing connection to AGIO Node at {url}...")
    result = node.summarize('Verify the sovereign agent economy.')
    print(result)
