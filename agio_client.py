import requests
import sys

class AgioNode:
    def __init__(self, node_url):
        self.node_url = node_url

    def summarize(self, text, payer="AG1..."):
        payload = {
            "type": "summarize",
            "text": text,
            "payment": {"amount": 5, "payer": payer}
        }
        return requests.post(f"{self.node_url}/task", json=payload).json()

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://[random-words].trycloudflare.com'
    node = AgioNode(url)
    print("Testing connection to Agio Network...")
    print(node.summarize('The agent economy starts here.'))
