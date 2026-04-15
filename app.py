from flask import Flask, jsonify, request, render_template
import websocket
import json
import threading
import numpy as np
import pandas as pd

app = Flask(__name__)

# ===============================
# 📊 MARKET DATA STORE
# ===============================
market_data = {
    "R_10": [],
    "R_25": [],
    "R_50": [],
    "R_100": []
}

# ===============================
# 🔌 DERIV WEBSOCKET
# ===============================
def start_ws(symbol):
    def on_message(ws, message):
        data = json.loads(message)

        if "tick" in data:
            price = data["tick"]["quote"]
            market_data[symbol].append(price)

            # Keep only last 200 prices
            if len(market_data[symbol]) > 200:
                market_data[symbol].pop(0)

    ws = websocket.WebSocketApp(
        "wss://ws.derivws.com/websockets/v3?app_id=1089",
        on_message=on_message
    )

    def on_open(ws):
        ws.send(json.dumps({
            "ticks": symbol,
            "subscribe": 1
        }))

    ws.on_open = on_open
    ws.run_forever()


def start_all():
    for pair in market_data.keys():
        threading.Thread(target=start_ws, args=(pair,), daemon=True).start()


# ===============================
# 🧠 SIMPLE AI ANALYSIS
# ===============================
def analyze(prices):
    if len(prices) < 10:
    return {
        "signal": "WAIT",
        "trend": "WAITING DATA",
        "entry": 0,
        "tp": 0,
        "sl": 0,
        "confidence": 0
    }

    current = prices[-1]
    avg = np.mean(prices[-20:])

    trend = "UPTREND" if current > avg else "DOWNTREND"

    signal = "WAIT"
    if current > avg:
        signal = "BUY"
    elif current < avg:
        signal = "SELL"

    entry = current
    tp = current + 5
    sl = current - 5

    confidence = int(abs(current - avg) * 10)
    if confidence > 95:
        confidence = 95

    return {
        "signal": signal,
        "trend": trend,
        "entry": round(entry, 2),
        "tp": round(tp, 2),
        "sl": round(sl, 2),
        "confidence": confidence
    }


# ===============================
# 🌐 ROUTES
# ===============================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan")
def scan():
    results = {}

    for pair, prices in market_data.items():
        data = analyze(prices)
        results[pair] = data if data else {
    "signal": "WAIT",
    "trend": "NO DATA",
    "entry": 0,
    "tp": 0,
    "sl": 0,
    "confidence": 0
}


@app.route("/connect", methods=["POST"])
def connect():
    try:
        data = request.json
        token = data.get("token")

        ws = websocket.WebSocket()
        ws.connect("wss://ws.derivws.com/websockets/v3?app_id=1089")

        ws.send(json.dumps({"authorize": token}))
        response = json.loads(ws.recv())

        if "error" in response:
            return jsonify({"error": "Invalid token"})

        account = response["authorize"]

        return jsonify({
            "loginid": account["loginid"],
            "balance": account["balance"],
            "currency": account["currency"]
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# ===============================
# 🚀 RUN
# ===============================
if __name__ == "__main__":
    start_all()
    app.run(debug=True)
