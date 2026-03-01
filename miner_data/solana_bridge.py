import time
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import subprocess

# 1. Connect to Solana Mainnet
solana_client = Client("https://api.mainnet-beta.solana.com")
MY_WALLET = Pubkey.from_string("AG103b72592445ccf687ab4e73824f001570a4f9")

print(f"[*] Monitoring Solana for Task Payments to: {MY_WALLET}")

def run_paid_task(prompt):
    print(f"[!] Payment Verified. Executing: {prompt}")
    res = subprocess.check_output(["ollama", "run", "qwen2.5:0.5b", prompt], text=True)
    return res

while True:
    # 2. Check for new transactions
    txs = solana_client.get_signatures_for_address(MY_WALLET, limit=1)
    if txs.value:
        latest_tx = txs.value[0].signature
        # In a real setup, you'd verify the amount here
        print(f"[+] New Payment Detected: {latest_tx}")
        
        # 3. Trigger the AI
        output = run_paid_task("Analyze this electrical circuit for safety.")
        print(f"Result: {output}")
        
    time.sleep(10) # Scan every 10 seconds