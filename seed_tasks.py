import sqlite3
import json

def initialize_and_seed():
    # Connects to agio.db (creates it if it doesn't exist)
    conn = sqlite3.connect('agio.db')
    c = conn.cursor()
    
    # 1. CREATE the table first (The Junction Box)
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_payload TEXT NOT NULL,
            validator_id TEXT NOT NULL,
            challenged INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. PREPARE the bait
    clean_task = json.dumps({"task": "Audit Code", "verified": True})
    malicious_task = json.dumps({"task": "Audit Code", "verified": False})
    
    # 3. INSERT the bait
    c.execute("INSERT INTO tasks (task_payload, validator_id) VALUES (?, ?)", (clean_task, "GoodNode_Alpha"))
    c.execute("INSERT INTO tasks (task_payload, validator_id) VALUES (?, ?)", (malicious_task, "LazyNode_Beta"))
    
    conn.commit()
    print("[SUCCESS] Grid Initialized: 'tasks' table created and bait deployed.")
    conn.close()

if __name__ == "__main__":
    initialize_and_seed()
