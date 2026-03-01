import sqlite3
from solana.rpc.api import Client
from solders.keypair import Keypair

# DATA FROM YOUR SCREENSHOT
PK_HEX = "25e7c70b82a0d0af89a4465dbbd0d0d6460e86c13f7536244aaa3b55258cd0d4"
PUBLIC_ADDR = "2ysSiSpaHAGaBmYJqBs3ueyfQn4uTHXwp33MQ6hQSsGN"

try:
    # 1. Pull Local Work (1,001 AGIO)
    conn = sqlite3.connect("agio.db")
    local_bal = conn.execute("SELECT balance FROM accounts WHERE address LIKE 'AG103b%'").fetchone()[0]
    conn.close()

    # 2. Reconstruct Keypair from Seed
    # Using 'from_seed' fixes the "length 64" error
    kp = Keypair.from_seed(bytes.fromhex(PK_HEX))
    
    # 3. Check Live Mainnet SOL
    client = Client("https://api.mainnet-beta.solana.com")
    sol_bal = client.get_balance(kp.pubkey()).value / 10**9

    print(f"\n--- VALLE-NET PRODUCTION AUDIT ---")
    print(f"AGIO (Local Ledger): {local_bal}")
    print(f"SOL  (Mainnet Fuel): {sol_bal}")
    print(f"Public Address:      {kp.pubkey()}")
    
    if sol_bal >= 0.01:
        print("\nSTATUS: [ SUCCESS ] - Ready to bridge 1,001 AGIO.")
    else:
        print(f"\nSTATUS: [ INSUFFICIENT FUEL ]")
        print(f"ACTION: Send 0.01 SOL to {kp.pubkey()} to enable bridge.")
except Exception as e:
    print(f"\nSYSTEM ERROR: {e}")
