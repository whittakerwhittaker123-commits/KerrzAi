from flask import Flask, render_template, jsonify
import websocket, json
import numpy as np

app = Flask(__name__)

DERIV_APP_ID = "1089"

PAIRS = ["R_10", "R_25", "R_50", "R_75", "R_100"]


# ---------- DERIV DATA ----------
def get_prices(symbol):
    ws = websocket.create_connection(
        f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}"
    )

    ws.send(json.dumps({
        "ticks_history": symbol,
        "count": 60,
        "end": "latest",
        "style": "ticks"
    }))

    res = json.loads(ws.recv())
    ws.close()

    return [float(p) for p in res["history"]["prices"]]


# ---------- INDICATORS ----------
def rsi(prices, period=14):
    deltas = np.diff(prices)
    gain = np.maximum(deltas, 0)
    loss = np.abs(np.minimum(deltas, 0))

    avg_gain = np.mean(gain[:period])
    avg_loss = np.mean(loss[:period])

    rs = avg_gain / (avg_loss + 1e-10)
    return 100 - (100 / (1 + rs))


def ema(prices, period=20):
    ema_vals = [prices[0]]
    k = 2 / (period + 1)

    for p in prices[1:]:
        ema_vals.append(p * k + ema_vals[-1] * (1 - k))

    return ema_vals


# ---------- SMART MONEY LOGIC ----------
def analyze(prices):

    rsi_val = rsi(prices)
    ema_vals = ema(prices)

    price = prices[-1]
    trend = "RANGE"

    if price > ema_vals[-1]:
        trend = "UPTREND"
    elif price < ema_vals[-1]:
        trend = "DOWNTREND"

    # BOS (structure break)
    high = max(prices[-10:])
    low = min(prices[-10:])

    bos = None
    if price > high:
        bos = "BOS_UP"
    elif price < low:
        bos = "BOS_DOWN"

    signal = "WAIT"

    # ENTRY LOGIC
    if trend == "UPTREND" and rsi_val < 40:
        signal = "BUY"
    elif trend == "DOWNTREND" and rsi_val > 60:
        signal = "SELL"

    # TP/SL
    vol = np.std(prices)

    if signal == "BUY":
        entry = price
        sl = entry - vol * 1.5
        tp = entry + vol * 3

    elif signal == "SELL":
        entry = price
        sl = entry + vol * 1.5
        tp = entry - vol * 3

    else:
        entry, tp, sl = price, "-", "-"

    confidence = min(95, int(abs(rsi_val - 50) * 2))

    return {
        "trend": trend,
        "signal": signal,
        "entry": round(entry, 2),
        "tp": round(tp, 2) if tp != "-" else "-",
        "sl": round(sl, 2) if sl != "-" else "-",
        "rsi": round(rsi_val, 2),
        "bos": bos,
        "confidence": confidence
    }


# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan")
def scan():
    results = {}

    for pair in PAIRS:
        try:
            prices = get_prices(pair)
            results[pair] = analyze(prices)
        except:
            results[pair] = {"error": "Data failed"}

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
