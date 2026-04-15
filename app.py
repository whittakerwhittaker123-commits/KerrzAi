from flask import Flask, jsonify, render_template
import websocket
import json
import numpy as np
import pandas as pd
import threading

app = Flask(__name__)

# ================================
# 📡 STORE LIVE DATA
# ================================
market_data = {
    "R_10": [],
    "R_25": [],
    "R_50": [],
    "R_75": [],
    "R_100": []
}

# ================================
# 📡 DERIV STREAM
# ================================
def start_ws(symbol):

    def on_message(ws, message):
        data = json.loads(message)

        if "tick" in data:
            price = data["tick"]["quote"]

            market_data[symbol].append(price)

            # keep last 200 points
            if len(market_data[symbol]) > 200:
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


def start_streams():
    for pair in market_data.keys():
        threading.Thread(target=start_ws, args=(pair,), daemon=True).start()

start_streams()


# ================================
# 📊 INDICATORS
# ================================
def calculate_rsi(prices, period=14):
    if len(prices) < period:
        return 50

    deltas = np.diff(prices)
    gains = np.maximum(deltas, 0)
    losses = np.abs(np.minimum(deltas, 0))

    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def calculate_ema(prices, period=20):
    if len(prices) < period:
        return prices[-1]

    return pd.Series(prices).ewm(span=period).mean().iloc[-1]


def calculate_atr(prices, period=14):
    if len(prices) < period:
        return 0

    trs = []
    for i in range(1, len(prices)):
        tr = max(
            abs(prices[i] - prices[i-1]),
            abs(prices[i] - prices[i-1]),
            abs(prices[i] - prices[i-1])
        )
        trs.append(tr)

    return np.mean(trs[-period:])


# ================================
# 🧠 AI ANALYSIS
# ================================
def analyze_market(prices):

    current = prices[-1]

    rsi = calculate_rsi(prices)
    ema = calculate_ema(prices)
    atr = calculate_atr(prices)

    # TREND
    trend = "UPTREND" if current > ema else "DOWNTREND"

    # BOS
    high = max(prices[-20:])
    low = min(prices[-20:])

    if current > high:
        bos = "BULLISH BOS"
    elif current < low:
        bos = "BEARISH BOS"
    else:
        bos = "NONE"

    # SIGNAL
    signal = "WAIT"

    if trend == "UPTREND" and rsi < 35:
        signal = "BUY 👇"
    elif trend == "DOWNTREND" and rsi > 65:
        signal = "SELL 👇"

    # ENTRY / SL / TP (REALISTIC)
    entry = current

    if "BUY" in signal:
        sl = entry - (atr * 2)
        tp = entry + (atr * 4)
    elif "SELL" in signal:
        sl = entry + (atr * 2)
        tp = entry - (atr * 4)
    else:
        sl = entry
        tp = entry

    confidence = int(min(95, abs(rsi - 50) * 2))

    return {
        "signal": signal,
        "trend": trend,
        "entry": round(entry, 2),
        "tp": round(tp, 2),
        "sl": round(sl, 2),
        "bos": bos,
        "rsi": rsi,
        "confidence": confidence
    }


# ================================
# 🌐 ROUTES
# ================================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signal/<pair>")
def signal(pair):

    prices = market_data.get(pair, [])

    if len(prices) < 50:
        return jsonify({"error": "Waiting for data..."})

    result = analyze_market(prices)

    return jsonify({
        "pair": pair,
        "prices": prices[-50:],
        "signal": result["signal"],
        "trend": result["trend"],
        "entry": result["entry"],
        "tp": result["tp"],
        "sl": result["sl"],
        "bos": result["bos"],
        "rsi": result["rsi"],
        "confidence": result["confidence"]
    })


# ================================
# 🚀 RUN
# ================================
if __name__ == "__main__":
    app.run()
