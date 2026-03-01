import threading, time

class AGIONode:
    def __init__(self, wallet, ledger, consensus=None, port=7400):
        self.wallet=wallet; self.ledger=ledger; self.port=port; self.running=False
    def start(self):
        self.running=True
        self.ledger.set_config("status","ACTIVE")
        self.ledger.set_config("node_address", self.wallet.address)
        threading.Thread(target=self._beat, daemon=True).start()
        print(f"[NODE] {self.wallet.address[:20]}... on 0.0.0.0:{self.port}")
    def _beat(self):
        while self.running:
            self.ledger.set_config("last_heartbeat", str(time.time()))
            time.sleep(30)
    @property
    def address(self): return self.wallet.address
