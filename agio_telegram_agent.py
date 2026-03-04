import os, sys, time, json, signal, sqlite3, requests

TOKEN = os.environ.get("TG_TOKEN", "").strip()
if not TOKEN:
    TOKEN = input("Paste your new BotFather token: ").strip()
if not TOKEN:
    print("ERROR: No token."); sys.exit(1)

BRIDGE_URL = "http://127.0.0.1:8402"
TASK_COST  = 10
FREE_AGIO  = 100
COOLDOWN_S = 15

try:
    import telebot
except ImportError:
    print("ERROR: pip install pyTelegramBotAPI"); sys.exit(1)

bot = telebot.TeleBot(TOKEN, parse_mode=None)

def shutdown(sig, frame):
    print("\n[BOT] Stopping...")
    try: bot.stop_polling()
    except: pass
    sys.exit(0)

signal.signal(signal.SIGINT,  shutdown)
signal.signal(signal.SIGTERM, shutdown)

_last_call = {}
def rate_limited(uid):
    now = time.time()
    last = _last_call.get(str(uid), 0)
    if now - last < COOLDOWN_S:
        return True, int(COOLDOWN_S - (now - last))
    _last_call[str(uid)] = now
    return False, 0

def get_db():
    conn = sqlite3.connect("ledger.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS wallets (
                agent_id TEXT PRIMARY KEY,
                balance REAL DEFAULT 0,
                total_tasks INTEGER DEFAULT 0,
                joined REAL
            );
        """)

def ensure_wallet(uid):
    conn = get_db()
    row = conn.execute("SELECT balance FROM wallets WHERE agent_id=?", (str(uid),)).fetchone()
    if row:
        conn.close(); return float(row["balance"])
    conn.execute("INSERT INTO wallets (agent_id,balance,joined) VALUES (?,?,?)",
                 (str(uid), FREE_AGIO, time.time()))
    conn.commit(); conn.close()
    return float(FREE_AGIO)

def debit(uid, amount):
    conn = get_db()
    row = conn.execute("SELECT balance FROM wallets WHERE agent_id=?", (str(uid),)).fetchone()
    if not row or float(row["balance"]) < amount:
        conn.close(); return False
    conn.execute("UPDATE wallets SET balance=balance-?, total_tasks=total_tasks+1 WHERE agent_id=?",
                 (amount, str(uid)))
    conn.commit(); conn.close(); return True

def call_bridge(text, uid):
    return requests.post(
        BRIDGE_URL + "/task",
        json={"type": "qa", "text": text,
              "payment": {"amount": TASK_COST, "payer": str(uid)}},
        timeout=120
    )

@bot.message_handler(commands=["start"])
def on_start(m):
    bal = ensure_wallet(m.from_user.id)
    bot.reply_to(m, "AV-001 ONLINE - AGIO Network\n\nBalance: " + str(int(bal)) + " AGIO\nCost: " + str(TASK_COST) + " AGIO per message\n\nPowered by Llama 3 | Thousand Oaks CA\n\n/balance  /sdk  /node  /help")

@bot.message_handler(commands=["balance"])
def on_balance(m):
    bal = ensure_wallet(m.from_user.id)
    bot.reply_to(m, "Balance: " + str(round(bal,1)) + " AGIO\nTasks remaining: " + str(int(bal // TASK_COST)))

@bot.message_handler(commands=["sdk"])
def on_sdk(m):
    bot.reply_to(m, "Agent-to-agent payments:\n\nimport requests\n\nrequests.post('" + BRIDGE_URL + "/task', json={\n  'type': 'qa',\n  'text': 'your question',\n  'payment': {'amount': 10, 'payer': 'your_agent_id'}\n})\n\nNo API key. Just AGIO.\ngithub.com/Darwin-Vallejos/agio-network")

@bot.message_handler(commands=["node"])
def on_node(m):
    try:
        r = requests.get(BRIDGE_URL + "/stats", timeout=5).json()
        bot.reply_to(m, "AGIO Node\nCompleted: " + str(r.get("completed", 0)) + " tasks\nSupply: " + str(int(r.get("total_supply", 0))) + " AGIO\nModel: Llama 3 | Thousand Oaks CA")
    except:
        bot.reply_to(m, "Node stats unavailable. Is x402_bridge running?")

@bot.message_handler(commands=["help"])
def on_help(m):
    bot.reply_to(m, "AV-001 real capabilities (Llama 3):\n\n+ Answer any question\n+ Write and debug code\n+ Crypto and DeFi explanations\n+ Summarize and translate\n+ Step-by-step reasoning\n\nCannot do: real-time data, images, transactions\n\nCost: " + str(TASK_COST) + " AGIO per message")

@bot.message_handler(func=lambda m: True)
def on_message(m):
    uid = m.from_user.id
    limited, wait = rate_limited(uid)
    if limited:
        bot.reply_to(m, "Wait " + str(wait) + "s before next message.")
        return
    bal = ensure_wallet(uid)
    if bal < TASK_COST:
        bot.reply_to(m, "Insufficient AGIO. Balance: " + str(round(bal,1)) + "\nNeed: " + str(TASK_COST) + " AGIO\nContact @DarwinVallejos to top up.")
        return
    status = bot.reply_to(m, "Computing on sovereign node...")
    try:
        r = call_bridge(m.text, uid)
        if r.status_code == 200:
            data = r.json()
            result = data.get("result", "No response")
            elapsed = data.get("elapsed_s", 0)
            debit(uid, TASK_COST)
            new_bal = bal - TASK_COST
            bot.edit_message_text(result + "\n\n[" + str(int(new_bal)) + " AGIO | " + str(round(elapsed,1)) + "s | Llama 3]", m.chat.id, status.message_id)
        elif r.status_code == 402:
            bot.edit_message_text("Payment error. Bridge restarting.", m.chat.id, status.message_id)
        elif r.status_code == 403:
            bot.edit_message_text("Auth error. Contact node operator.", m.chat.id, status.message_id)
        else:
            bot.edit_message_text("Node error " + str(r.status_code) + ". Try again.", m.chat.id, status.message_id)
    except requests.exceptions.Timeout:
        bot.edit_message_text("Llama 3 is thinking. Try a shorter question.", m.chat.id, status.message_id)
    except requests.exceptions.ConnectionError:
        bot.edit_message_text("Bridge offline. Start x402_bridge.py first.", m.chat.id, status.message_id)
    except Exception as e:
        print("[ERROR] " + str(e))
        bot.edit_message_text("Node error. Try again in 30 seconds.", m.chat.id, status.message_id)

if __name__ == "__main__":
    init_db()
    print("AGIO TELEGRAM BOT v3.0")
    print("Bridge: " + BRIDGE_URL)
    print("Cost: " + str(TASK_COST) + " AGIO/message")
    print("Bot active. Ctrl+C to stop cleanly.")
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except KeyboardInterrupt:
            shutdown(None, None)
        except Exception as e:
            print("[POLL ERROR] " + str(e) + " - retrying in 5s")
            time.sleep(5)

