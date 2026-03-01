import sqlite3, time

MINT = "5YAJCvod5W8tzfrVZfZC1X4vnFWSshCZyXfhg9frLx8z"
WALLET = "2ysSiSpaHAGaBmYJqBs3ueyfQn4uTHXwp33MQ6hQSsGN"

con = sqlite3.connect("agio.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS node_config (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
for k, v in {
    "status": "ACTIVE",
    "stake_mint": MINT,
    "stake_amount": "1001.0",
    "wallet": WALLET,
    "activated_at": str(time.time())
}.items():
    cur.execute("INSERT INTO node_config(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (k,v))
con.commit()
con.close()
print("[NODE] LURKING -> ACTIVE")
print(f"[MINT] {MINT}")
