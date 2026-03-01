from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solana.rpc.types import TokenAccountOpts

addr = "2ysSiSpaHAGaBmYJqBs3ueyfQn4uTHXwp33MQ6hQSsGN"
client = Client("https://api.mainnet-beta.solana.com")
owner_pubkey = Pubkey.from_string(addr)

try:
    # 1. Check SOL Balance
    balance = client.get_balance(owner_pubkey).value / 10**9
    print(f"\n--- MAINNET TRUTH REPORT ---")
    print(f"Address:     {addr}")
    print(f"SOL Balance: {balance} SOL")
    
    # 2. Check for Token Accounts (FIXED ENCODING)
    # We use the standard SPL Token Program ID
    opts = TokenAccountOpts(program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), encoding="jsonParsed")
    tokens = client.get_token_accounts_by_owner(owner_pubkey, opts)
    
    print(f"Token Accounts: {len(tokens.value) if tokens.value else 0}")
    
    for acc in tokens.value:
        mint = acc.account.data.parsed['info']['mint']
        amount = acc.account.data.parsed['info']['tokenAmount']['uiAmount']
        print(f"-> MINT: {mint} | BALANCE: {amount} AGIO")

    if balance > 0:
        print("\nSTATUS: Circuit is Hot. Connection Verified.")
except Exception as e:
    print(f"SYSTEM ERROR: {e}")
