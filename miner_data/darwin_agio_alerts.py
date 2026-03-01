import time
import requests
import os

# 1. Your Connection Point
DISCORD_WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"

def send_alert(message):
    payload = {"content": f"🚀 **AGIO BOUNTY ALERT**\n{message}"}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

print("[*] Monitoring Challenger Logs for Slashes...")

# 2. The Logic: Watch the Log for "Slash" or "Bounty"
log_path = "node.log"

while True:
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            lines = f.readlines()
            for line in lines[-5:]: # Check the last 5 entries
                if "SLASH_EVENT" in line or "BOUNTY_CLAIMED" in line:
                    print(f"[!] New Bounty Detected: {line.strip()}")
                    send_alert(f"Node AG103b... just claimed a bounty!\nDetails: {line.strip()}")
    
    time.sleep(60) # Check every minute to save Lenovo CPU