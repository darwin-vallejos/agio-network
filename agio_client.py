"""
AGIO Client SDK
Lets any AI agent hire your Thousand Oaks node for inference.
Usage:
    from agio_client import AgioNode
    node = AgioNode('https://your-node-url.ngrok-free.app')
    result = node.summarize('Your text here')
"""
import requests, json

class AgioNode:
    PRICES = {'summarize':5,'code':15,'compute':10,'verify':5,'translate':8}

    def __init__(self, endpoint):
        self.base = endpoint.rstrip('/')

    def status(self):
        return requests.get(self.base, timeout=10).json()

    def summarize(self, text, payer='agent', amount=5):
        return self._task('summarize', text, payer, amount)

    def code(self, description, payer='agent', amount=15):
        return self._task('code', description, payer, amount)

    def verify(self, claim, payer='agent', amount=5):
        return self._task('verify', claim, payer, amount)

    def compute(self, expression, payer='agent', amount=10):
        return self._task('compute', expression, payer, amount)

    def translate(self, text, payer='agent', amount=8):
        return self._task('translate', text, payer, amount)

    def _task(self, task_type, text, payer, amount):
        required = self.PRICES.get(task_type, 10)
        if amount < required:
            return {'error': f'Minimum payment is {required} AGIO for {task_type}'}
        try:
            # FIXED: Pointing to /tasks to match the live x402_bridge.py
            r = requests.post(f'{self.base}/tasks', json={
                'type': task_type,
                'text': text,
                'payment': {'amount': amount, 'payer': payer}
            }, timeout=60)
            return r.json()
        except Exception as e:
            return {'error': str(e)}

if __name__ == '__main__':
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else input('Node URL: ')
    node = AgioNode(url)
    print('Connecting to AGIO node...')
    try:
        # Simple status check
        print(json.dumps(node.status(), indent=2))
        print('\nRunning test task...')
        result = node.summarize(
            'AGIO is the economic layer that lets AI agents pay each other for verified work.',
            payer='sdk_test'
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Connection failed: {e}")
