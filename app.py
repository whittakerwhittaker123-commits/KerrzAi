from flask import Flask, jsonify, render_template, request
import numpy as np
import websocket
import json
import threading

app = Flask(__name__)

# ===============================
# 📡 STORE MARKET DATA
# ===============================
market_data = {
    "R_10": [],
    "R_25": [],
    "R_50": [],
    "R_75": [],
    "R_100": []
}

# ===============================
# 📡 DERIV WEBSOCKET
# ===============================
def start_ws(symbol):

    def on_message(ws, message):
        data = json.loads(message)

        if "tick" in data:
            price = data["tick"]["quote"]

            market_data[symbol].append(price)

            # keep last 100 prices only
            if len(market_data[symbol]) > 100:
                market_data[symbol].pop(0)

    def on_open(ws):
        ws.send(json.dumps({
            "ticks": symbol,
            "subscribe": 1
        }))

    ws = websocket.WebSocketApp(
        "wss://ws.derivws.com/websockets/v3?app_id=1089",
        on_message=on_message,
        on_open=on_open
    )

    ws.run_forever()


# start all pairs
for pair in market_data:
    threading.Thread(target=start_ws, args=(pair,), daemon=True).start()


# ===============================
# 📊 INDICATORS
# ===============================
def ema(prices, period=10):
    if len(prices) < period:
        return None
    return np.mean(prices[-period:])


def rsi(prices, period=14):
    if len(prices) < period:
        return 50

    delta = np.diff(prices)
    gain = np.maximum(delta, 0)
    loss = np.abs(np.minimum(delta, 0))

    avg_gain = np.mean(gain[-period:])
    avg_loss = np.mean(loss[-period:]) + 1e-9

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def atr(prices, period=14):
    if len(prices) < period:
        return 0

    diffs = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
    return np.mean(diffs[-period:])


# ===============================
# 🧠 ANALYSIS ENGINE
# ===============================
def analyze(pair, prices):

    if len(prices) < 20:
        return None

    current = prices[-1]

    # indicators
    ema_val = ema(prices)
    rsi_val = rsi(prices)
    atr_val = atr(prices)

    # trend
    trend = "UPTREND" if current > ema_val else "DOWNTREND"

    # signal logic
    if trend == "UPTREND" and rsi_val < 40:
        signal = "BUY"
    elif trend == "DOWNTREND" and rsi_val > 60:
        signal = "SELL"
    else:
        signal = "WAIT"

    # 🔥 FIXED SL/TP (ATR BASED — NOT TOO TIGHT)
    if signal == "BUY":
        entry = current
        sl = current - (atr_val * 2)
        tp = current + (atr_val * 4)
    elif signal == "SELL":
        entry = current
        sl = current + (atr_val * 2)
        tp = current - (atr_val * 4)
    else:
        entry = tp = sl = 0

    # confidence
    confidence = int(abs(rsi_val - 50) * 2)

    return {
        "pair": pair,
        "trend": trend,
        "signal": signal,
        "entry": round(entry, 2),
        "tp": round(tp, 2),
        "sl": round(sl, 2),
        "bos": "N/A",
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

    mode = request.args.get("mode", "Sniper")
    min_conf = int(request.args.get("min_conf", 70))

    results = {}

    for pair, prices in market_data.items():

        data = analyze(pair, prices)

        if not data:
            continue

        # filter by confidence
        if data["confidence"] < min_conf:
            continue

        results[pair] = data

    return jsonify(results)


# ===============================
# 🚀 RUN
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
