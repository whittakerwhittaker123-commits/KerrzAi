from flask import Flask, jsonify, render_template, request
import numpy as np
import websocket
import json
import threading

app = Flask(__name__)

# ===============================
# 📡 MARKET DATA STORE
# ===============================
market_data = {
    "R_10": [],
    "R_25": [],
    "R_50": [],
    "R_75": [],
    "R_100": []
}

# ===============================
# 📡 DERIV LIVE DATA
# ===============================
def start_ws(symbol):

    def on_message(ws, message):
        data = json.loads(message)

        if "tick" in data:
            price = data["tick"]["quote"]
            market_data[symbol].append(price)

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


for pair in market_data:
    threading.Thread(target=start_ws, args=(pair,), daemon=True).start()


# ===============================
# 📊 INDICATORS
# ===============================
def ema(prices, period=20):
    return np.mean(prices[-period:]) if len(prices) >= period else prices[-1]


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
# 🕯 CANDLE PATTERNS
# ===============================
def bullish_engulfing(prices):
    if len(prices) < 3:
        return False
    return prices[-1] > prices[-2] and prices[-2] < prices[-3]


def bearish_engulfing(prices):
    if len(prices) < 3:
        return False
    return prices[-1] < prices[-2] and prices[-2] > prices[-3]


# ===============================
# 🧠 SMART MONEY LOGIC
# ===============================
def break_of_structure(prices):
    if len(prices) < 20:
        return "NONE"

    recent_high = max(prices[-20:-5])
    recent_low = min(prices[-20:-5])
    current = prices[-1]

    if current > recent_high:
        return "BULLISH BOS"
    elif current < recent_low:
        return "BEARISH BOS"
    else:
        return "NONE"


# ===============================
# 🔥 MAIN AI ANALYSIS
# ===============================
def analyze(pair, prices):

    if len(prices) < 10:
    return {
        "pair": pair,
        "trend": "LOADING...",
        "signal": "WAIT",
        "entry": 0,
        "tp": 0,
        "sl": 0,
        "bos": "N/A",
        "confidence": 0
    }

    current = prices[-1]

    # indicators
    ema_val = ema(prices)
    rsi_val = rsi(prices)
    atr_val = atr(prices)

    bos = break_of_structure(prices)

    # trend
    trend = "UPTREND" if current > ema_val else "DOWNTREND"

    # patterns
    bull = bullish_engulfing(prices)
    bear = bearish_engulfing(prices)

    # ===============================
    # 🎯 SIGNAL LOGIC (LEVEL 3)
    # ===============================
    signal = "WAIT"

    if trend == "UPTREND" and rsi_val < 40 and bull:
        signal = "BUY"

    elif trend == "DOWNTREND" and rsi_val > 60 and bear:
        signal = "SELL"

    # ===============================
    # 💰 ENTRY / SL / TP
    # ===============================
    entry = current

    if signal == "BUY":
        sl = entry - (atr_val * 2)
        tp = entry + (atr_val * 4)

    elif signal == "SELL":
        sl = entry + (atr_val * 2)
        tp = entry - (atr_val * 4)

    else:
        sl = tp = 0

    # ===============================
    # 📊 CONFIDENCE SYSTEM
    # ===============================
    confidence = 50

    if trend == "UPTREND" or trend == "DOWNTREND":
        confidence += 10

    if bull or bear:
        confidence += 15

    if bos != "NONE":
        confidence += 15

    confidence = min(confidence, 95)

    return {
        "pair": pair,
        "trend": trend,
        "signal": signal,
        "entry": round(entry, 2),
        "tp": round(tp, 2),
        "sl": round(sl, 2),
        "bos": bos,
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
    min_conf = int(request.args.get("min_conf", 60))

    results = {}

    for pair, prices in market_data.items():

        data = analyze(pair, prices)

        if not data:
            continue

        if data["confidence"] < min_conf:
            continue

        results[pair] = data

    return jsonify(results)


# ===============================
# 🚀 RUN
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
