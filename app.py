import os
import json
import websocket
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

DERIV_APP_ID = "1089"

def get_prices(symbol):
    prices = []
    try:
        ws = websocket.create_connection(
            f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}"
        )

        ws.send(json.dumps({
            "ticks": symbol,
            "subscribe": 1
        }))

        for _ in range(30):
            data = json.loads(ws.recv())
            prices.append(data["tick"]["quote"])

        ws.close()
        return prices

    except:
        return []


def calculate_rsi(prices, period=14):
    if len(prices) < period:
        return 50

    gains, losses = [], []

    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff >= 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = sum(gains) / period if gains else 0.01
    avg_loss = sum(losses) / period if losses else 0.01

    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


@app.route("/")
def home():
    return render_template("index.html")


@@app.route("/signal")
def signal():
    symbol = request.args.get("symbol", "R_100")

    prices = get_prices(symbol)

    if len(prices) < 10:
        return jsonify({"error": "Not enough data"})

    rsi = calculate_rsi(prices)

    if rsi < 30:
        signal = "BUY"
    elif rsi > 70:
        signal = "SELL"
    else:
        signal = "WAIT"

    return jsonify({
        "prices": prices,
        "rsi": rsi,
        "signal": signal
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
