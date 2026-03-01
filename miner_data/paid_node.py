from fastapi import FastAPI, Request, HTTPException
import subprocess
import stripe
import sqlite3

app = FastAPI()

# Your Stripe Secret Key (found at dashboard.stripe.com/apikeys)
stripe.api_key = "sk_test_your_key_here"

def update_ledger(amount):
    """Updates your local SQLite balance to reflect real-world earnings."""
    conn = sqlite3.connect('agio.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE wallet SET balance = balance + ? WHERE id = 1", (amount,))
    conn.commit()
    conn.close()

@app.post("/infer")
async def infer(request: Request):
    data = await request.json()
    payment_id = data.get("payment_id")
    prompt = data.get("prompt")

    # 1. Real-World Payment Verification
    try:
        # Retrieve the payment status from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_id)
        if intent.status != "succeeded":
            return {"error": "Payment required or failed"}
    except Exception as e:
        raise HTTPException(status_code=402, detail=f"Stripe Error: {str(e)}")

    # 2. Local AI Execution (Qwen 2.5)
    result = subprocess.run(
        ["ollama", "run", "qwen2.5:0.5b", prompt],
        capture_output=True, text=True
    )

    # 3. Ledger Update
    update_ledger(1) # Log 1 "AGIO" credit earned per transaction
    
    return {"response": result.stdout.strip()}

if __name__ == "__main__":
    import uvicorn
    # Use 0.0.0.0 to allow external connections from the web
    uvicorn.run(app, host="0.0.0.0", port=8000)