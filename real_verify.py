import sqlite3
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solders.message import Message

# 1. SETUP
PK_HEX = "25e7c70b82a0d0af89a4465dbbd0d0d6460e86c13f7536244aaa3b55258cd0d4"
client = Client("https://api.mainnet-beta.solana.com")
kp = Keypair.from_seed(bytes.fromhex(PK_HEX))

try:
    # Get local record
    conn = sqlite3.connect("agio.db")
    local_bal = conn.execute("SELECT balance FROM accounts WHERE address LIKE 'AG103b%'").fetchone()[0]
    conn.close()

    print(f"--- ATTEMPTING LIVE MAINNET HANDSHAKE ---")
    blockhash = client.get_latest_blockhash().value.blockhash
    
    # This is a REAL instruction to the System Program
    # We send a tiny 'heartbeat' to verify the broadcast circuit
    ix = transfer(TransferParams(from_pubkey=kp.pubkey(), to_pubkey=kp.pubkey(), lamports=1000))
    msg = Message([ix], kp.pubkey())
    tx = Transaction([kp], msg, blockhash)
    
    # BROADCAST
    result = client.send_transaction(tx)
    
    print(f"\n[ BROADCAST SUCCESSFUL ]")
    print(f"REAL Transaction Signature: {result.value}")
    print(f"Verify on Solscan: https://solscan.io/tx/{result.value}")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
