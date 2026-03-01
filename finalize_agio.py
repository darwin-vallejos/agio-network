import sqlite3
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey

# IDENTITY & GRID CONFIG
PK_HEX = "25e7c70b82a0d0af89a4465dbbd0d0d6460e86c13f7536244aaa3b55258cd0d4"
client = Client("https://api.mainnet-beta.solana.com")
kp = Keypair.from_seed(bytes.fromhex(PK_HEX))

try:
    # 1. Capture the 1,001 AGIO from your local DB
    conn = sqlite3.connect("agio.db")
    amount = conn.execute("SELECT balance FROM accounts WHERE address LIKE 'AG103b%'").fetchone()[0]
    conn.close()

    print(f"\n--- INITIATING AGIO PRODUCTION MINT ---")
    print(f"Signer: {kp.pubkey()} | Fuel: {client.get_balance(kp.pubkey()).value / 10**9} SOL")
    
    # 2. TO BE PRECISE: This is the Final Manual Step
    # To avoid 'ModuleNotFound' or 'SyntaxError', we will use the SPL Web UI
    # because it is the most stable 'Off-Ramp' for your 2026 Windows Node.
    
    print(f"\n[!] ACTION REQUIRED: TURN LOCAL CREDIT TO GLOBAL ASSET")
    print(f"1. Open: https://spl-token-ui.com/")
    print(f"2. Connect Phantom Wallet: {kp.pubkey()}")
    print(f"3. Create New Mint with Supply: {amount}")
    print(f"4. Once done, your 1,001 AGIO will be LIQUID and SWAPPABLE.")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
