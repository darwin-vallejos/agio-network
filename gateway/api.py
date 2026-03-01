import json, time, uuid, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

class GatewayHandler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _j(self, code, body):
        data = json.dumps(body, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length", len(data))
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers(); self.wfile.write(data)
    def _body(self):
        n = int(self.headers.get("Content-Length",0))
        return json.loads(self.rfile.read(n) or b"{}") if n else {}
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers()
    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/")
        ledger, wallet = self.server.ledger, self.server.wallet
        if path in ("","/" ,"/status"):
            self._j(200, {"node":wallet.address,"status":"ACTIVE","balance":ledger.balance(wallet.address),**ledger.stats()})
        elif path == "/tasks":
            tasks = ledger.get_pending_tasks()
            self._j(200, {"tasks":tasks,"count":len(tasks)})
        elif path.startswith("/balance/"):
            addr = path.split("/balance/")[1]
            self._j(200, {"address":addr,"balance":ledger.balance(addr)})
        elif path == "/stats":
            self._j(200, ledger.stats())
        else:
            self._j(404, {"error":"not found"})
    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/")
        body = self._body()
        ledger, wallet = self.server.ledger, self.server.wallet
        if path == "/tasks":
            tid = str(uuid.uuid4())
            ttype = body.get("task_type","summarize")
            payload = body.get("payload",{})
            if not payload: self._j(400,{"error":"payload required"}); return
            ledger.create_task(tid, ttype, json.dumps(payload), body.get("requester","agent"), float(body.get("reward",10)), int(body.get("difficulty",1)))
            print(f"[TASK] {ttype} reward={body.get('reward',10)} id={tid[:16]}...")
            self._j(201, {"success":True,"task_id":tid})
        elif "/claim" in path:
            tid = path.split("/tasks/")[1].split("/claim")[0]
            agent = body.get("agent_address","")
            ok = ledger.claim_task(tid, agent)
            self._j(200 if ok else 409, {"success":ok,"task_id":tid})
        elif "/submit" in path:
            tid = path.split("/tasks/")[1].split("/submit")[0]
            result = body.get("result","")
            if not result: self._j(400,{"error":"result required"}); return
            out = ledger.complete_task(tid, result)
            if out.get("success"):
                print(f"[DONE] {tid[:16]}... +{out['agio_earned']} AGIO bal={out['new_balance']:.1f}")
            self._j(200 if out.get("success") else 400, out)
        else:
            self._j(404, {"error":"not found"})

def start_gateway(node, ledger, exchange, pow_engine, wallet, port=7500):
    srv = HTTPServer(("0.0.0.0", port), GatewayHandler)
    srv.ledger = ledger; srv.wallet = wallet; srv.node = node
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"[GATEWAY] HTTP API on http://0.0.0.0:{port}")
    return srv
