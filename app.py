import os
import json
import websocket
import threading
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

DERIV_APP_ID = "1089"

# 🔥 STORE LIVE PRICES
price_data = {
    "R_100": [],
    "R_50": [],
    "R_25": [],
    "R_10": [],
    "R_75": []
}


# ✅ BACKGROUND STREAM (SAFE LOOP)
def stream_prices(symbol):
    while True:
        try:
            ws = websocket.create_connection(
                f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}"
            )

            ws.send(json.dumps({
                "ticks": symbol,
                "subscribe": 1
            }))

            while True:
                data = json.loads(ws.recv())

                # ✅ SAFE CHECK
                if "tick" in data and "quote" in data["tick"]:
                    price = data["tick"]["quote"]

                    price_data[symbol].append(price)

                    if len(price_data[symbol]) > 50:
                        price_data[symbol].pop(0)

        except Exception as e:
            print(f"Stream error ({symbol}):", e)
            continue  # reconnect automatically


# ✅ START THREADS SAFELY
def start_streams():
    for symbol in price_data.keys():
        t = threading.Thread(target=stream_prices, args=(symbol,))
        t.daemon = True
        t.start()


# ✅ RSI CALCULATION
def calculate_rsi(prices, period=14):
    if len(prices) < period:
        return 50

    gains = []
    losses = []

    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff >= 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = sum(gains) / period if gains else 0.01
    avg_loss = sum(losses) / period if losses else 0.01

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return round(rsi, 2)


# ✅ ROUTES
@app.route("/signal")
def signal():
    try:
        symbol = request.args.get("symbol", "R_100")
        prices = price_data.get(symbol, [])

        if len(prices) < 10:
            return jsonify({
                "prices": prices,
                "rsi": 50,
                "signal": "WAIT"
            })

        rsi = calculate_rsi(prices)

        if rsi < 30:
            sig = "BUY"
        elif rsi > 70:
            sig = "SELL"
        else:
            sig = "WAIT"

        return jsonify({
            "prices": prices,
            "rsi": rsi,
            "signal": sig
        })

    except Exception as e:
        print("Signal error:", e)
        return jsonify({
            "prices": [],
            "rsi": 50,
            "signal": "WAIT"
        })


# ✅ START STREAMS AFTER APP LOAD (IMPORTANT FIX)
@app.before_request
def start_background():
    global started
    if not started:
        start_streams()
        started = True


# ✅ RUN APP
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
