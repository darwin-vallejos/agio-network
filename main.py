import sqlite3, requests, json, hashlib, time, os
from flask import Flask, request, jsonify
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError

app = Flask(__name__)
NODE_KEY_PATH = "node_data/wallet.json"
MODEL_NAME = "llama3.2"
DEX_API = "https://api.dexscreener.com/latest/dex/search?q="

def canonical(obj): return json.dumps(obj, separators=(",", ":"), sort_keys=True)

def load_or_create_node_key():
    os.makedirs("node_data", exist_ok=True)
    if os.path.exists(NODE_KEY_PATH):
        with open(NODE_KEY_PATH) as f: w = json.load(f)
        return SigningKey(bytes.fromhex(w["sk_hex"])), w["pk_hex"]
    sk = SigningKey.generate()
    w = {"sk_hex": sk.encode().hex(), "pk_hex": sk.verify_key.encode().hex()}
    with open(NODE_KEY_PATH, "w") as f: json.dump(w, f, indent=2)
    return sk, w["pk_hex"]

NODE_SK, NODE_PK = load_or_create_node_key()

def init_db():
    conn = sqlite3.connect("ledger.db")
    conn.execute('CREATE TABLE IF NOT EXISTS wallets (agent_id TEXT PRIMARY KEY, balance REAL)')
    conn.execute('CREATE TABLE IF NOT EXISTS receipts (task_id TEXT PRIMARY KEY, receipt_hash TEXT, agent_id TEXT, payment REAL, timestamp REAL)')
    conn.commit()
    conn.close()

def fetch_dex_alpha(query):
    try:
        r = requests.get(f"{DEX_API}{query}", timeout=10)
        pairs = [p for p in r.json().get('pairs', []) if p.get('chainId') == 'solana'][:3]
        res = []
        for p in pairs:
            liq = float(p.get('liquidity', {}).get('usd', 0))
            score = 40 if liq < 20000 else 0
            res.append({"symbol": p.get('baseToken',{}).get('symbol'), "address": p.get('pairAddress'), "liquidity": liq, "risk_score": score})
        return res
    except: return []

@app.route('/status', methods=['GET'])
def get_status():
    conn = sqlite3.connect("ledger.db")
    count = conn.execute("SELECT COUNT(*) FROM receipts").fetchone()[0]
    conn.close()
    return jsonify({"node_id": NODE_PK, "status": "ONLINE", "settled_receipts": count})

@app.route('/task', methods=['POST'])
def handle_task():
    req_data = request.json.get("request", {})
    sig = req_data.pop("signature", None)
    requester_pk = req_data.get("requester")
    task_id = req_data.get("task_id")
    payment = float(req_data.get("payment", 10.0))
    prompt = req_data.get("prompt", "")

    if not sig or not requester_pk or not task_id: return jsonify({"error": "Malformed request"}), 400

    try: VerifyKey(bytes.fromhex(requester_pk)).verify(canonical(req_data).encode(), bytes.fromhex(sig))
    except: return jsonify({"error": "Invalid signature"}), 401

    conn = sqlite3.connect("ledger.db")
    cursor = conn.cursor()
    try: cursor.execute("INSERT INTO receipts (task_id, receipt_hash, agent_id, payment, timestamp) VALUES (?, 'PENDING', ?, ?, ?)", (task_id, requester_pk, payment, time.time()))
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Replay attack detected"}), 403

    row = cursor.execute("SELECT balance FROM wallets WHERE agent_id=?", (requester_pk,)).fetchone()
    bal = row[0] if row else 100.0
    if bal < payment:
        cursor.execute("DELETE FROM receipts WHERE task_id=?", (task_id,))
        conn.commit()
        conn.close()
        return jsonify({"error": "Insufficient AGIO"}), 402

    if any(k in prompt.lower() for k in ["alpha", "scan", "pair"]):
        raw_data = fetch_dex_alpha(prompt)
        ai_prompt = f"SYSTEM: Analyze this DexScreener JSON deterministically. DATA: {json.dumps(raw_data)}\nUSER: {prompt}"
    else:
        ai_prompt = f"SYSTEM: Direct professional response.\nUSER: {prompt}"

    try:
        r = requests.post("http://localhost:11434/api/generate", json={"model": MODEL_NAME, "prompt": ai_prompt, "stream": False}, timeout=120)
        ai_res = r.json().get("response")
    except: ai_res = "Inference Engine Offline."

    new_bal = bal - payment
    cursor.execute("INSERT OR REPLACE INTO wallets (agent_id, balance) VALUES (?, ?)", (requester_pk, new_bal))
    
    signed_response = {"task_id": task_id, "result": ai_res, "timestamp": time.time(), "node_id": NODE_PK}
    res_msg = canonical(signed_response).encode()
    receipt_hash = hashlib.sha256(res_msg).hexdigest()
    signed_response["signature"] = NODE_SK.sign(res_msg).signature.hex()

    cursor.execute("UPDATE receipts SET receipt_hash=? WHERE task_id=?", (receipt_hash, task_id))
    conn.commit()
    conn.close()

    return jsonify({"result": ai_res, "signed_response": signed_response, "node_id": NODE_PK, "receipt_hash": receipt_hash, "protocol": "SRP-v1"})

if __name__ == '__main__':
    init_db()
    print(f"─── SRP-v1 NODE READY | ID: {NODE_PK[:16]}... ───")
    app.run(port=8402)
