import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from http.server import HTTPServer, BaseHTTPRequestHandler
from core.wallet import AGIOWallet
from core.ledger_db import PersistentLedger
from core.ai_worker import process_task, check_ollama

PRICES = {"summarize":5,"code":15,"verify":5,"compute":10,"translate":8,"qa":7}

class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def _j(self,code,body):
        data=json.dumps(body,indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",len(data))
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers(); self.wfile.write(data)
    def _body(self):
        n=int(self.headers.get("Content-Length",0))
        return json.loads(self.rfile.read(n) or b"{}") if n else {}
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers()
    def do_GET(self):
        w,l = self.server.wallet, self.server.ledger
        self._j(200,{"node":w.address,"balance":l.balance(w.address),"pricing":PRICES,"ollama":check_ollama()["status"],"status":"online","protocol":"x402","usage":{"POST /task":{"type":"summarize|code|verify|compute|qa","text":"your text","payment":{"amount":5,"payer":"AG1..."}}}})
    def do_POST(self):
        w,l = self.server.wallet, self.server.ledger
        b = self._body()
        ttype = b.get("type","summarize")
        text = b.get("text") or b.get("prompt") or str(b.get("payload",""))
        payment = b.get("payment",{})
        amount = float(payment.get("amount",0))
        required = PRICES.get(ttype,10)
        if amount < required:
            self._j(402,{"error":"Payment Required","required":required,"asset":"AGIO","recipient":w.address,"pricing":PRICES}); return
        if not text:
            self._j(400,{"error":"text required"}); return
        t0=time.time()
        result=process_task(ttype,{"text":text})
        elapsed=time.time()-t0
        l.mint_reward(w.address, amount, f"x402:{ttype}")
        bal=l.balance(w.address)
        print(f"[x402] +{amount} AGIO | {ttype} | {elapsed:.1f}s | balance={bal:.1f}")
        self._j(200,{"result":result,"elapsed_s":round(elapsed,2),"payment":f"+{amount} AGIO accepted","node_balance":bal,"protocol":"x402"})

d=json.load(open("miner_data/wallet.json"))
wallet=AGIOWallet(sk_hex=d.get("sk_hex") or d.get("_value",""))
ledger=PersistentLedger("agio.db")
print("─── AGIO x402 BRIDGE ───")
print(f"[*] Node:    {wallet.address}")
print(f"[*] Balance: {ledger.balance(wallet.address):.1f} AGIO")
print(f"[*] Ollama:  {check_ollama()['status']}")
print(f"[*] Port:    8402")
print(f"[*] Waiting for agent payments...")
srv=HTTPServer(("0.0.0.0",8402),H)
srv.wallet=wallet; srv.ledger=ledger
try: srv.serve_forever()
except KeyboardInterrupt: print("Bridge stopped.")
