from flask import Flask, jsonify

app = Flask(__name__)

app.route('/')
def home():
    return  "App is live 🚀"
    <html>
<head>
<title>KerrzAI</title>

<style>
body {
    margin:0;
    font-family:Arial;
    background:#0f172a;
    color:white;
}

.header {
    padding:20px;
    font-size:24px;
}

.grid {
    display:grid;
    grid-template-columns: repeat(2, 1fr);
    gap:15px;
    padding:20px;
}

.card {
    background:#1f2937;
    padding:15px;
    border-radius:12px;
}

.buy { color:lime; }
.sell { color:red; }
</style>
</head>

<body>

<div class="header">KerrzAI 🤖</div>

<div class="grid" id="marketGrid"></div>

<script>
async function loadSignals() {
    let res = await fetch('/signals');
    let data = await res.json();

    let html = "";

    data.forEach(pair => {
        html += `
        <div class="card">
            <h3>${pair.name}</h3>
            <p class="${pair.signal.toLowerCase()}">${pair.signal}</p>
            <p>RSI: ${pair.rsi}</p>
        </div>
        `;
    });

    document.getElementById("marketGrid").innerHTML = html;
}

setInterval(loadSignals, 3000);
loadSignals();
</script>

</body>
</html>
    '''

app.route('/signals')
def signals():
    return jsonify([
        {"name": "Vol 10", "signal": "BUY", "rsi": 28},
        {"name": "Vol 25", "signal": "SELL", "rsi": 65},
        {"name": "Vol 50", "signal": "BUY", "rsi": 32},
        {"name": "Vol 75", "signal": "SELL", "rsi": 70},
        {"name": "Vol 100", "signal": "BUY", "rsi": 25}
    ])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
