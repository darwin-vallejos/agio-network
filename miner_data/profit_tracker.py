import time
import os

# Current Market Estimations (Feb 28, 2026)
AGIO_TO_USD = 0.082  # Each AGIO is roughly 8 cents
STAKE_AMOUNT = 1001
REPUTATION = 550.0

def get_session_stats():
    # In a real setup, this reads your node.log for [SUCCESS] messages
    # For now, we calculate your active potential
    audits_completed = 0
    with open("node.log", "r") as f:
        for line in f:
            if "Audit passed" in line:
                audits_completed += 1
    return audits_completed

while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    audits = get_session_stats()
    agio_earned = audits * 5
    usd_value = agio_earned * AGIO_TO_USD
    
    print("─── VALLE-NET REAL-TIME REVENUE ───")
    print(f"[*] Node Identity: AG103b... (Thousand Oaks)")
    print(f"[*] Reputation:    {REPUTATION} (ESTABLISHED)")
    print(f"[*] Current Stake: {STAKE_AMOUNT} AGIO")
    print("───────────────────────────────────")
    print(f" [!] Total Audits: {audits}")
    print(f" [!] AGIO Earned:  {agio_earned} AGIO")
    print(f" [!] USD Value:    ${usd_value:.2f}")
    print("───────────────────────────────────")
    print("Status: COLLECTING FEES...")
    
    time.sleep(30)