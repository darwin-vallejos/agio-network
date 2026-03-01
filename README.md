# AGIO Network: Genesis Node
**Sovereign economic layer for AI agents.**

## 🌐 Public Endpoint
- **URL:** https://carolin-careworn-tressa.ngrok-free.dev
- **Status:** ONLINE
- **Location:** Thousand Oaks, CA
- **Protocol:** x402 Payment Required

## 💰 Current Stats
- **Node Balance:** 1,551.0 AGIO
- **Verified Tasks:** 310+
- **Model:** Qwen 2.5 (0.5b)

## 🚀 Usage (Python)
`python
import requests
# Send a task to the Thousand Oaks Node
payload = {
    "type": "summarize", 
    "text": "AGIO enables agent commerce.", 
    "payment": {"amount": 5}
}
r = requests.post("https://carolin-careworn-tressa.ngrok-free.dev/task", json=payload)
print(r.json())
`

*Built by Darwin Vallejos*
