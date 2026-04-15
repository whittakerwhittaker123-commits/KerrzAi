from flask import Flask, render_template, request, jsonify
import websocket
import json
import numpy as np
import time

app = Flask(__name__)

DERIV_APP_ID = "1089"

@app.route("/")
def home():
    return render_template("index.html")


# ---------- GET LIVE DATA FROM DERIV ----------
def get_deriv_prices(symbol="R_100", count=50):
    prices = []

    ws = websocket.create_connection(
        f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}"
    )

    ws.send(json.dumps({
        "ticks_history": symbol,
        "count": count,
        "end": "latest",
        "style": "ticks"
    }))

    result = json.loads(ws.recv())

    ws.close()

    for tick in result["history"]["prices"]:
        prices.append(float(tick))

    return prices


# ---------- INDICATORS ----------
def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    gain = np.maximum(deltas, 0)
    loss = np.abs(np.minimum(deltas, 0))

    avg_gain = np.mean(gain[:period])
    avg_loss = np.mean(loss[:period])

    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))

    return round(rsi, 2)


def calculate_ema(prices, period=20):
    ema = [prices[0]]
    k = 2 / (period + 1)

    for price in prices[1:]:
        ema.append(price * k + ema[-1] * (1 - k))

    return ema


# ---------- AI ANALYSIS ----------
def analyze_market(prices):

    rsi = calculate_rsi(prices)
    ema = calculate_ema(prices)

    price = prices[-1]
    ema_now = ema[-1]

    trend = "RANGE"
    signal = "WAIT"

    # TREND
    if price > ema_now:
        trend = "UPTREND"
    elif price < ema_now:
        trend = "DOWNTREND"

    # ENTRY LOGIC
    if trend == "UPTREND" and rsi < 35:
        signal = "BUY"
    elif trend == "DOWNTREND" and rsi > 65:
        signal = "SELL"

    # TP / SL
    volatility = np.std(prices)

    if signal == "BUY":
        entry = price
        sl = entry - volatility * 1.5
        tp = entry + volatility * 3

    elif signal == "SELL":
        entry = price
        sl = entry + volatility * 1.5
        tp = entry - volatility * 3

    else:
        entry, tp, sl = price, "-", "-"

    return {
        "trend": trend,
        "signal": signal,
        "entry": round(entry, 2),
        "tp": round(tp, 2) if tp != "-" else "-",
        "sl": round(sl, 2) if sl != "-" else "-",
        "rsi": rsi
    }


# ---------- API ROUTE ----------
@app.route("/signal")
def signal():
    symbol = request.args.get("symbol", "R_100")

    try:
        prices = get_deriv_prices(symbol)
        analysis = analyze_market(prices)

        return jsonify({
            "prices": prices,
            **analysis
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True)
