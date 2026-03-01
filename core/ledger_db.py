import sqlite3, time, threading

class PersistentLedger:
    def __init__(self, db_path="agio.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init()
    def _conn(self):
        c = sqlite3.connect(self.db_path, check_same_thread=False)
        c.row_factory = sqlite3.Row
        return c
    def _init(self):
        with self._lock:
            c = self._conn()
            c.executescript("""
                CREATE TABLE IF NOT EXISTS balances (address TEXT PRIMARY KEY, balance REAL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, recipient TEXT, amount REAL, memo TEXT, ts REAL);
                CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, task_type TEXT, payload TEXT, requester TEXT, reward REAL DEFAULT 10, difficulty INTEGER DEFAULT 1, status TEXT DEFAULT 'pending', assigned_to TEXT DEFAULT '', result TEXT DEFAULT '', submitted_at REAL, claimed_at REAL, completed_at REAL);
                CREATE TABLE IF NOT EXISTS node_config (key TEXT PRIMARY KEY, value TEXT);
            """)
            c.commit(); c.close()
    def balance(self, addr):
        with self._lock:
            c = self._conn()
            r = c.execute("SELECT balance FROM balances WHERE address=?", (addr,)).fetchone()
            c.close()
            return float(r["balance"]) if r else 0.0
    def genesis(self, allocs):
        with self._lock:
            c = self._conn()
            for addr, amt in allocs.items():
                if not c.execute("SELECT 1 FROM balances WHERE address=?", (addr,)).fetchone():
                    c.execute("INSERT INTO balances VALUES (?,?)", (addr, amt))
                    c.execute("INSERT INTO transactions (sender,recipient,amount,memo,ts) VALUES (?,?,?,?,?)", ("GENESIS",addr,amt,"genesis",time.time()))
            c.commit(); c.close()
    def mint_reward(self, addr, amt, memo="reward"):
        with self._lock:
            c = self._conn()
            c.execute("INSERT INTO balances (address,balance) VALUES (?,?) ON CONFLICT(address) DO UPDATE SET balance=balance+?", (addr,amt,amt))
            c.execute("INSERT INTO transactions (sender,recipient,amount,memo,ts) VALUES (?,?,?,?,?)", ("MINT",addr,amt,memo,time.time()))
            c.commit(); c.close()
    def get_pending_tasks(self):
        with self._lock:
            c = self._conn()
            rows = c.execute("SELECT * FROM tasks WHERE status='pending' ORDER BY submitted_at").fetchall()
            c.close()
            return [dict(r) for r in rows]
    def create_task(self, tid, ttype, payload, requester, reward, difficulty=1):
        with self._lock:
            c = self._conn()
            c.execute("INSERT OR IGNORE INTO tasks (task_id,task_type,payload,requester,reward,difficulty,submitted_at) VALUES (?,?,?,?,?,?,?)", (tid,ttype,payload,requester,reward,difficulty,time.time()))
            c.commit(); c.close()
    def claim_task(self, tid, agent):
        with self._lock:
            c = self._conn()
            r = c.execute("SELECT status FROM tasks WHERE task_id=?", (tid,)).fetchone()
            if not r or r["status"] != "pending":
                c.close(); return False
            c.execute("UPDATE tasks SET status='claimed',assigned_to=?,claimed_at=? WHERE task_id=? AND status='pending'", (agent,time.time(),tid))
            c.commit(); c.close(); return True
    def complete_task(self, tid, result):
        with self._lock:
            c = self._conn()
            r = c.execute("SELECT * FROM tasks WHERE task_id=?", (tid,)).fetchone()
            if not r or r["status"] != "claimed":
                c.close(); return {"success":False,"message":"not claimed"}
            agent, reward = r["assigned_to"], float(r["reward"])
            c.execute("UPDATE tasks SET status='completed',result=?,completed_at=? WHERE task_id=?", (result,time.time(),tid))
            c.execute("INSERT INTO balances (address,balance) VALUES (?,?) ON CONFLICT(address) DO UPDATE SET balance=balance+?", (agent,reward,reward))
            c.execute("INSERT INTO transactions (sender,recipient,amount,memo,ts) VALUES (?,?,?,?,?)", ("REWARD",agent,reward,f"task:{tid}",time.time()))
            c.commit()
            bal = float(c.execute("SELECT balance FROM balances WHERE address=?", (agent,)).fetchone()["balance"])
            c.close()
            return {"success":True,"agio_earned":reward,"new_balance":bal}
    def stats(self):
        with self._lock:
            c = self._conn()
            s = {"total_supply": c.execute("SELECT COALESCE(SUM(balance),0) FROM balances").fetchone()[0],
                 "total_tasks": c.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],
                 "completed": c.execute("SELECT COUNT(*) FROM tasks WHERE status='completed'").fetchone()[0]}
            c.close(); return s
    def set_config(self, k, v):
        with self._lock:
            c = self._conn()
            c.execute("INSERT INTO node_config VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=?", (k,v,v))
            c.commit(); c.close()
