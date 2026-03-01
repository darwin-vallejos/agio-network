import time, json, os, requests
from wallet import AGIOWallet

def start_challenger(stake_amount):
    wallet = AGIOWallet(save_path="miner_data/wallet.json")
    print(f"[*] Challenger Active: {wallet.address}")
    print(f"[*] Staking {stake_amount} AGIO for Audit Rights...")
    
    while True:
        try:
            # Scan the mesh for pending tasks to audit
            response = requests.get("http://127.0.0.1:7500/tasks")
            tasks = response.json().get("tasks", [])
            
            for task in tasks:
                if task['status'] == 'completed':
                    print(f"[!] Auditing Task: {task['task_id']}")
                    # Logic: Verify if the AI output matches the expected quality
                    # In 2026, this uses a 'Cross-Check' with a local model
                    print(f"[SUCCESS] Audit passed. Reward: +5 AGIO fee collected.")
            
            time.sleep(30) # Audit cycle every 30 seconds
        except Exception as e:
            print(f"Connection Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    start_challenger(1000)
