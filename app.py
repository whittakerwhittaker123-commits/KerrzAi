from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signal")
def signal():
    symbol = request.args.get("symbol")

    # Fake market data (simulate AI)
    prices = [round(100 + random.uniform(-5, 5), 2) for _ in range(30)]

    trend = random.choice(["UPTREND", "DOWNTREND", "RANGE"])
    signal = random.choice(["BUY", "SELL", "WAIT"])

    entry = round(prices[-1], 2)
    tp = round(entry + random.uniform(5, 15), 2)
    sl = round(entry - random.uniform(5, 15), 2)

    return jsonify({
        "symbol": symbol,
        "trend": trend,
        "signal": signal,
        "entry": entry,
        "tp": tp,
        "sl": sl,
        "prices": prices
    })

if __name__ == "__main__":
    app.run(debug=True)
