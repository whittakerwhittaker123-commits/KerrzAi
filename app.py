from flask import Flask, jsonify, render_template, request
import numpy as np
import websocket
import json
import threading
TOKENS = {
    "demo": "YOUR_DEMO_TOKEN",
    "real": "REAL_TOKEN"
}
account_info = {
    "balance": 0,
    "currency": "USD"
}

imports

app = Flask(__name__)

functions (analyze, etc)

@app.route("/")        ✅
@app.route("/connect") ✅ ← HERE
@app.route("/scan")    ✅

if __name__ == "__main__":
    app.run()

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

    import websocket
import json

def on_message(ws, message):
    try:
        data = json.loads(message)

        # ✅ HANDLE LOGIN RESPONSE
        if "authorize" in data:
            print("✅ Logged in:", data["authorize"]["loginid"])
            print("💰 Balance:", data["authorize"]["balance"])

        # ✅ HANDLE PRICE DATA
        if "tick" in data:
            price = data["tick"]["quote"]

            market_data[symbol].append(price)

            if len(market_data[symbol]) > 200:
                market_data[symbol].pop(0)

    except Exception as e:
        print("❌ Error:", e)


def on_open(ws):
    # 🔐 LOGIN TO DERIV ACCOUNT
    ws.send(json.dumps({
        "authorize": DERIV_TOKEN
    }))

    # 📡 SUBSCRIBE TO LIVE DATA
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
def ema(prices, period=20):
    if len(prices) < period:
        return prices[-1]
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
        return 1  # prevent zero SL

    diffs = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
    return np.mean(diffs[-period:])


# ===============================
# 🕯 PATTERNS
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
# 🧠 BOS (SMART MONEY)
# ===============================
def break_of_structure(prices):
    if len(prices) < 20:
        return "NONE"

    high = max(prices[-20:-5])
    low = min(prices[-20:-5])
    current = prices[-1]

    if current > high:
        return "BULLISH BOS"
    elif current < low:
        return "BEARISH BOS"
    return "NONE"


# ===============================
# 🔥 AI ANALYSIS
# ===============================
def analyze(pair, prices):

    # 🔥 FIX: ALWAYS RETURN DATA (no blank UI)
    if len(prices) < 10:
        return {
            "pair": pair,
            "trend": "WAITING DATA",
            "signal": "WAIT",
            "entry": 0,
            "tp": 0,
            "sl": 0,
            "bos": "N/A",
            "confidence": 0
        }

    current = prices[-1]

    ema_val = ema(prices)
    rsi_val = rsi(prices)
    atr_val = atr(prices)
    bos = break_of_structure(prices)

    trend = "UPTREND" if current > ema_val else "DOWNTREND"

    bull = bullish_engulfing(prices)
    bear = bearish_engulfing(prices)

    signal = "WAIT"

    if trend == "UPTREND" and rsi_val < 40 and bull:
        signal = "BUY"

    elif trend == "DOWNTREND" and rsi_val > 60 and bear:
        signal = "SELL"

    # ===============================
    # 💰 ENTRY / TP / SL
    # ===============================
    entry = current

    if signal == "BUY":
        sl = entry - (atr_val * 2)
        tp = entry + (atr_val * 4)

    elif signal == "SELL":
        sl = entry + (atr_val * 2)
        tp = entry - (atr_val * 4)

    else:
        sl = entry
        tp = entry

    # ===============================
    # 📊 CONFIDENCE
    # ===============================
    confidence = 50

    if signal != "WAIT":
        confidence += 20

    if bos != "NONE":
        confidence += 15

    if bull or bear:
        confidence += 15

    confidence = min(confidence, 95)

    return {
        "pair": pair,
        "trend": trend,
        "signal": signal,
        "entry": round(entry, 2),
        "tp": round(tp, 4),
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

from flask import request, jsonify

@app.route("/connect", methods=["POST"])
def connect():
    try:
        data = request.json
        token = data.get("token")

        import websocket
        import json

        ws = websocket.WebSocket()
        ws.connect("wss://ws.derivws.com/websockets/v3?app_id=1089")

        # Send token
        ws.send(json.dumps({"authorize": token}))

        response = json.loads(ws.recv())

        print("DERIV RESPONSE:", response)

        if "error" in response:
            return jsonify({"error": "Invalid token"})

        account = response["authorize"]

        return jsonify({
            "balance": account.get("balance", 0),
            "currency": account.get("currency", "USD"),
            "loginid": account.get("loginid", "Unknown")
        })

    except Exception as e:
        print("CONNECT ERROR:", str(e))
        return jsonify({"error": str(e)})
@app.route("/scan")
def scan():
    results = {}

    for pair, prices in market_data.items():

        if len(prices) < 20:
            results[pair] = {
                "signal": "WAIT",
                "trend": "WAITING DATA",
                "entry": 0,
                "tp": 0,
                "sl": 0,
                "bos": "NONE",
                "confidence": 0
            }
            continue

        data = analyze(prices)

        results[pair] = {
            "signal": data["signal"],
            "trend": data["trend"],
            "entry": data["entry"],
            "tp": data["tp"],
            "sl": data["sl"],
            "bos": data["bos"],
            "confidence": data["confidence"]
        }

    return jsonify(results)


# ===============================
# 🚀 RUN
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
