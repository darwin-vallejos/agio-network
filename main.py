import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.wallet import AGIOWallet
from core.ledger_db import PersistentLedger
from core.pow import ProofOfWork
from network.consensus import ConsensusEngine
from network.node import AGIONode
from gateway.api import start_gateway

WALLET_PATH = "miner_data/wallet.json"

def load_or_create_wallet():
    os.makedirs("miner_data", exist_ok=True)
    if os.path.exists(WALLET_PATH):
        try:
            d = json.load(open(WALLET_PATH))
            sk = d.get("sk_hex") or d.get("_value") or ""
            if sk: return AGIOWallet(sk_hex=sk)
        except: pass
    w = AGIOWallet.generate()
    json.dump(w.to_dict(), open(WALLET_PATH,"w"), indent=2)
    return w

wallet = load_or_create_wallet()
ledger = PersistentLedger("agio.db")
if ledger.balance(wallet.address) == 0:
    ledger.genesis({wallet.address: 1001})
bal = ledger.balance(wallet.address)
print("─── AGIO SOVEREIGN NODE V2.0 ───")
print(f"[*] Identity: {wallet.address}")
print(f"[*] Balance:  {bal:,.1f} AGIO")
print(f"[*] Status:   ACTIVE")
print("────────────────────────────────")
node = AGIONode(wallet, ledger, ConsensusEngine(wallet, ledger), port=7400)
node.start()
start_gateway(node, ledger, None, ProofOfWork(ledger), wallet, port=7500)
print("[*] HTTP API -> http://0.0.0.0:7500")
print("[*] Node ready. Windows 2 and 3 can start.")
try:
    while True:
        time.sleep(10)
        s = ledger.stats()
        if s["total_tasks"] > 0:
            print(f"[STATS] tasks={s['total_tasks']} done={s['completed']} supply={s['total_supply']:.1f} AGIO")
except KeyboardInterrupt:
    print("Shutdown.")
