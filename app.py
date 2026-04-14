from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head>
    <title>KerrzAI</title>
    <style>
    body {
        margin:0;
        font-family:Arial;
        background:#0f172a;
        color:white;
        display:flex;
    }

    .sidebar {
        width:30%;
        background:#111827;
        padding:20px;
    }

    .main {
        width:70%;
        padding:20px;
    }

    .card {
        background:#1f2937;
        padding:15px;
        margin-bottom:15px;
        border-radius:10px;
    }

    .buy {background:green; padding:15px; border-radius:10px; text-align:center;}
    .sell {background:red; padding:15px; border-radius:10px; text-align:center;}

    button {
        padding:10px;
        margin:5px;
        border:none;
        border-radius:5px;
        width:100%;
    }
    </style>
    </head>

    <body>

    <div class="sidebar">
        <h2>⚙️ Strategies</h2>

        <div class="card">RSI Strategy ✅</div>
        <div class="card">Trend Strategy ⬜</div>
        <div class="card">AI Filter ⬜</div>
    </div>

    <div class="main">
        <h1>KerrzAI 🤖</h1>

        <div class="card">
            📊 Live Chart (coming soon)
        </div>

        <div class="card" id="signalBox">
            Loading signal...
        </div>

        <div class="buy">BUY</div>
        <div class="sell">SELL</div>

    </div>

    <script>
    async function loadSignal(){
        let res = await fetch('/signal');
        let data = await res.json();

        document.getElementById("signalBox").innerHTML = `
            Signal: ${data.signal || data.status}<br>
            RSI: ${data.rsi || "-"}
        `;
    }

    setInterval(loadSignal, 3000);
    loadSignal();
    </script>

    </body>
    </html>
    '''

@app.route('/signal')
def signal():
    return jsonify({
        "signal": "BUY",
        "rsi": 28
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
