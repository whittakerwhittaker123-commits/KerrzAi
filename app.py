import os
import json
import websocket-client
from flask import Flask, jsonify, render_template

app = Flask(__name__)

DERIV_APP_ID = "1089"  # public test app id


def get_price():
    try:
        ws = websocket.create_connection(
            f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}"
        )

        request = {
            "ticks": "R_100",
            "subscribe": 1
        }

        ws.send(json.dumps(request))
        result = json.loads(ws.recv())
        ws.close()

        return result["tick"]["quote"]

    except:
        return None


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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signal")
def signal():
    prices = []

    for _ in range(20):
        price = get_price()
        if price:
            prices.append(price)

    if len(prices) == 0:
        return jsonify({"error": "No data"})

    rsi = calculate_rsi(prices)

    if rsi < 30:
        signal = "BUY"
    elif rsi > 70:
        signal = "SELL"
    else:
        signal = "WAIT"

    return jsonify({
        "rsi": rsi,
        "signal": signal
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
