from flask import Flask, jsonify
from websocket import WebSocketApp
import json

app = Flask(__name__)

price_data = []

def on_message(ws, message):
    global price_data
    data = json.loads(message)

    if "tick" in data:
        price = data["tick"]["quote"]
        price_data.append(price)

        if len(price_data) > 50:
            price_data.pop(0)

def get_rsi():
    if len(price_data) < 14:
        return None

    gains = []
    losses = []

    for i in range(1, len(price_data)):
        diff = price_data[i] - price_data[i-1]
        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = sum(gains)/len(gains) if gains else 0
    avg_loss = sum(losses)/len(losses) if losses else 1

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

@app.route('/signal')
def signal():
    rsi = get_rsi()

    if rsi is None:
        return jsonify({"status": "Collecting data..."})

    if rsi < 30:
        return jsonify({"signal": "BUY", "rsi": round(rsi,2)})
    elif rsi > 70:
        return jsonify({"signal": "SELL", "rsi": round(rsi,2)})
    else:
        return jsonify({"signal": "WAIT", "rsi": round(rsi,2)})

def start_ws():
    ws = WebSocketApp(
        "wss://ws.derivws.com/websockets/v3?app_id=1089",
        on_message=on_message
    )

    ws.on_open = lambda ws: ws.send(json.dumps({
        "ticks": "R_50"
    }))

    ws.run_forever()

import threading
threading.Thread(target=start_ws).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
