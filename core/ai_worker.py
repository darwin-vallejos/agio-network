import subprocess, json, urllib.request, urllib.error, time

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:0.5b"
TIMEOUT = 90
PROMPTS = {
    "summarize":  "Summarize in 2 clear sentences: {text}",
    "code":       "Write a clean Python function for: {text}",
    "verify":     "Is this true or false? Explain briefly: {text}",
    "compute":    "Calculate step by step: {text}",
    "translate":  "Translate to Spanish: {text}",
    "qa":         "Answer concisely: {text}",
}

def run_inference(prompt):
    try:
        payload = json.dumps({"model":MODEL,"prompt":prompt,"stream":False,"options":{"temperature":0.3,"num_predict":256}}).encode()
        req = urllib.request.Request(OLLAMA_API, data=payload, headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read()).get("response","").strip()
    except:
        try:
            r = subprocess.run(["ollama","run",MODEL,prompt], capture_output=True, timeout=TIMEOUT, text=True)
            return r.stdout.strip() or "No output"
        except Exception as e:
            return f"Ollama error: {e}"

def process_task(task_type, payload):
    text = payload.get("text") or payload.get("prompt") or str(payload)
    prompt = PROMPTS.get(task_type, "{text}").format(text=text)
    return run_inference(prompt)

def check_ollama():
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            models = [m["name"] for m in data.get("models",[])]
            return {"status": "ready" if any(MODEL in m for m in models) else f"{MODEL} not pulled", "models": models}
    except Exception as e:
        return {"status": f"offline: {e}"}
