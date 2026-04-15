from flask import Flask, jsonify, render_template
import websocket, json, threading
import numpy as np
import pandas as pd

app = Flask(__name__)

# ======================
# 📡 STORE DATA
# ======================
market_data = {
    "R_10": [], "R_25": [], "R_50": [], "R_75": [], "R_100": []
}

# ======================
# 📡 DERIV LIVE DATA
# ======================
def start_ws(symbol):
    def on_message(ws, message):
        data = json.loads(message)

        if "tick" in data:
            price = data["tick"]["quote"]
            market_data[symbol].append(price)

            if len(market_data[symbol]) > 200:
                market_data[symbol].pop(0)

    def on_open(ws):
        ws.send(json.dumps({"ticks": symbol, "subscribe": 1}))

    ws = websocket.WebSocketApp(
        "wss://ws.derivws.com/websockets/v3?app_id=1089",
        on_message=on_message,
        on_open=on_open
    )

    ws.run_forever()

def start_all():
    for pair in market_data:
        threading.Thread(target=start_ws, args=(pair,), daemon=True).start()

start_all()

# ======================
# 📊 INDICATORS
# ======================
def rsi(prices, period=14):
    if len(prices) < period:
        return 50

    delta = np.diff(prices)
    gain = np.maximum(delta, 0)
    loss = np.abs(np.minimum(delta, 0))

    rs = np.mean(gain[-period:]) / (np.mean(loss[-period:]) + 1e-9)
    return round(100 - (100 / (1 + rs)), 2)

def ema(prices, period=20):
    return pd.Series(prices).ewm(span=period).mean().iloc[-1]

def atr(prices, period=14):
    if len(prices) < period:
        return 0

    trs = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
    return np.mean(trs[-period:])

# ======================
# 🧠 ANALYSIS
# ======================
def analyze(prices):
    if len(prices) < 50:
        return None

    current = prices[-1]

    trend = "UPTREND" if current > ema(prices) else "DOWNTREND"

    high = max(prices[-20:])
    low = min(prices[-20:])

    bos = "NONE"
    if current > high:
        bos = "BULLISH BOS"
    elif current < low:
        bos = "BEARISH BOS"

    r = rsi(prices)

    signal = "WAIT"

    if trend == "UPTREND" and r < 40:
        signal = "BUY 👇"

    elif trend == "DOWNTREND" and r > 60:
        signal = "SELL 👇"

    a = atr(prices)
    entry = current

    if "BUY" in signal:
        sl = entry - (a * 2)
        tp = entry + (a * 3)

    elif "SELL" in signal:
        sl = entry + (a * 2)
        tp = entry - (a * 3)

    else:
        sl = entry
        tp = entry

    confidence = 50
    if signal != "WAIT":
        confidence += 20
    if bos != "NONE":
        confidence += 10

    confidence = min(confidence, 95)

    return {
        "signal": signal,
        "trend": trend,
        "entry": round(entry, 2),
        "tp": round(tp, 2),
        "sl": round(sl, 2),
        "bos": bos,
        "rsi": r,
        "confidence": confidence
    }

# ======================
# 🌐 ROUTES
# ======================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scan")
def scan():
    results = {}

    for pair, prices in market_data.items():
        data = analyze(prices)

        if data:
            results[pair] = data

    return jsonify(results)

# ======================
# 🚀 RUN
# ======================
if __name__ == "__main__":
    app.run()
