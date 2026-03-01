import sqlite3
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solders.message import Message

# PRODUCTION CONFIG
PK_HEX = "25e7c70b82a0d0af89a4465dbbd0d0d6460e86c13f7536244aaa3b55258cd0d4"
RPC_URL = "https://api.mainnet-beta.solana.com"

try:
    client = Client(RPC_URL)
    kp = Keypair.from_seed(bytes.fromhex(PK_HEX))
    blockhash = client.get_latest_blockhash().value.blockhash
    
    print(f"\n--- ATTEMPTING LIVE MAINNET BROADCAST ---")
    
    # Constructing a real instruction
    ix = transfer(TransferParams(
        from_pubkey=kp.pubkey(), 
        to_pubkey=kp.pubkey(), 
        lamports=1000 # Tiny 0.000001 SOL test pulse
    ))
    
    # Build and Sign
    msg = Message([ix], kp.pubkey())
    tx = Transaction([kp], msg, blockhash)
    
    # BROADCAST
    result = client.send_transaction(tx)
    
    print(f"\n[ BROADCAST SUCCESSFUL ]")
    print(f"REAL Transaction Signature: {result.value}")
    print(f"Verify here: https://solscan.io/tx/{result.value}")

except Exception as e:
    print(f"\nCRITICAL BROADCAST ERROR: {e}")
