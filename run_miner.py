import sys, os, time, json, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.wallet import AGIOWallet
from core.ai_worker import process_task, check_ollama

API = "http://127.0.0.1:7500"

def get(path):
    try:
        with urllib.request.urlopen(f"{API}{path}", timeout=10) as r: return json.loads(r.read())
    except Exception as e: return {"error":str(e)}

def post(path, body):
    try:
        data = json.dumps(body).encode()
        req = urllib.request.Request(f"{API}{path}", data=data, headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read())
    except Exception as e: return {"error":str(e)}

d = json.load(open("miner_data/wallet.json"))
wallet = AGIOWallet(sk_hex=d.get("sk_hex") or d.get("_value",""))
print("─── AGIO MINER ───")
print(f"[*] Miner:  {wallet.address}")
print(f"[*] Ollama: {check_ollama()['status']}")

for _ in range(30):
    if "node" in get("/status"): print("[*] Node online"); break
    time.sleep(2)
else:
    print("[!] Node not responding. Start main.py first."); sys.exit(1)

earned = 0
while True:
    try:
        tasks = get("/tasks").get("tasks",[])
        if not tasks:
            post("/tasks",{"task_type":"summarize","payload":{"text":"AGIO is the economic layer that lets AI agents pay each other for verified work without a human credit card or API key in the loop."},"requester":wallet.address,"reward":20,"difficulty":1})
            time.sleep(3); continue
        t = tasks[0]
        tid, ttype, payload, reward = t["task_id"], t.get("task_type","summarize"), json.loads(t.get("payload","{}")), t.get("reward",10)
        print(f"[->] {tid[:20]}... [{ttype}] reward={reward}")
        if not post(f"/tasks/{tid}/claim", {"agent_address":wallet.address}).get("success"):
            time.sleep(1); continue
        t0 = time.time()
        result = process_task(ttype, payload)
        elapsed = time.time()-t0
        r = post(f"/tasks/{tid}/submit", {"sk_hex":wallet.sk_hex(),"result":result})
        if r.get("success"):
            e = r.get("agio_earned",0); earned += e
            print(f"  [+] +{e} AGIO | {elapsed:.1f}s | session={earned:.1f} | balance={r.get('new_balance',0):.1f}")
            print(f"  [>] {result[:100]}{'...' if len(result)>100 else ''}\n")
        time.sleep(4)
    except KeyboardInterrupt: print(f"\nSession: +{earned} AGIO"); break
    except Exception as e: print(f"[!] {e}"); time.sleep(4)
