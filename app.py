from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route("/")
def signal():
    signal = random.choice(["BUY", "SELL"])

    entry = 42000

    if signal == "BUY":
        sl = entry - 1000
        tp = entry + 2000
    else:
        sl = entry + 1000
        tp = entry - 2000

    return jsonify({
        "signal": signal,
        "entry": entry,
        "sl": sl,
        "tp": tp
    })
