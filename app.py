from flask import Flask, jsonify, render_template
import websocket
import json
import numpy as np

app = Flask(__name__)

DERIV_APP_ID = 1089


# ================================
# 📡 GET REAL DERIV PRICES
# ================================

def get_deriv_prices(symbol="R_100", count=100):
    ws = websocket.create_connection(
        f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}"
    )

    # Request tick history
    ws.send(json.dumps({
        "ticks_history": symbol,
        "count": count,
        "end": "latest",
        "style": "ticks"
    }))

    data = json.loads(ws.recv())
    ws.close()

    prices = data["history"]["prices"]
    return prices


# ================================
# 📊 INDICATORS
# ================================

def calculate_rsi(prices, period=14):
    prices = np.array(prices)
    deltas = np.diff(prices)

    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_atr(prices, period=14):
    prices = np.array(prices)

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
# 🧠 SMART MONEY AI
# ================================

def detect_trend(prices):
    ema_fast = np.mean(prices[-10:])
    ema_slow = np.mean(prices[-30:])
    return "UPTREND" if ema_fast > ema_slow else "DOWNTREND"


def detect_bos(prices):
    if prices[-1] > max(prices[-20:-1]):
        return "BULLISH BOS"
    elif prices[-1] < min(prices[-20:-1]):
        return "BEARISH BOS"
    return "NONE"


def detect_candle(prices):
    return "BULLISH" if prices[-1] > prices[-2] else "BEARISH"


def analyze_market(prices):
    prices = np.array(prices)

    trend = detect_trend(prices)
    bos = detect_bos(prices)
    candle = detect_candle(prices)
    rsi = calculate_rsi(prices)
    atr = calculate_atr(prices)

    entry = prices[-1]

    # SIGNAL LOGIC
    if trend == "UPTREND" and rsi < 35:
        signal = "BUY"
    elif trend == "DOWNTREND" and rsi > 65:
        signal = "SELL"
    else:
        signal = "WAIT"

    # SL / TP (REAL)
    if signal == "BUY":
        sl = entry - (atr * 1.5)
        tp = entry + (atr * 3)
    elif signal == "SELL":
        sl = entry + (atr * 1.5)
        tp = entry - (atr * 3)
    else:
        sl = entry
        tp = entry

    confidence = int(min(95, abs(rsi - 50) + abs(entry - prices[-10])))

    return {
        "trend": trend,
        "signal": signal,
        "entry": round(entry, 2),
        "tp": round(tp, 2),
        "sl": round(sl, 2),
        "bos": bos,
        "candle": candle,
        "rsi": round(rsi, 2),
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
    try:
        prices = get_deriv_prices(pair)

        result = analyze_market(prices)

        return jsonify({
            "pair": pair,
            "signal": result["signal"],
            "trend": result["trend"],
            "entry": result["entry"],
            "tp": result["tp"],
            "sl": result["sl"],
            "bos": result["bos"],
            "candle": result["candle"],
            "rsi": result["rsi"],
            "confidence": result["confidence"],
            "prices": prices
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# ================================
# 🚀 RUN
# ================================

if __name__ == "__main__":
    app.run()
