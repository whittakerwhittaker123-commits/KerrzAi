from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>KerrzAI</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            body {
                font-family: Arial;
                background: #f5f5f5;
                padding: 10px;
                text-align: center;
            }

            h1 {
                margin-bottom: 10px;
            }

            button {
                padding: 10px;
                border: none;
                border-radius: 8px;
                background: black;
                color: white;
                margin-bottom: 15px;
            }

            .grid {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
            }

            .card {
                width: 48%;
                background: white;
                border-radius: 12px;
                padding: 10px;
                margin-bottom: 10px;
                border: 2px solid #ccc;
                text-align: left;
            }

            .buy { border-color: blue; }
            .sell { border-color: red; }
            .wait { border-color: orange; }

            .badge {
                padding: 5px;
                border-radius: 6px;
                color: white;
                display: inline-block;
                margin-top: 5px;
                font-size: 12px;
            }

            .blue { background: blue; }
            .red { background: red; }
            .orange { background: orange; }

            small {
                display: block;
                font-size: 11px;
                margin-top: 5px;
            }
        </style>
    </head>

    <body>

        <h1>KerrzAI 🤖</h1>

        <button onclick="scan()">Scan Markets</button>

        <div class="grid" id="signals"></div>

        <script>
        function scan() {
            const pairs = [
                "Vol 10","Vol 25","Vol 50","Vol 75",
                "Jump 25","Jump 50","Jump 100","Step Index"
            ];

            let html = "";

            pairs.forEach(pair => {

                let rsi = Math.floor(Math.random()*100);

                let signal = "WAIT";
                let cls = "wait";
                let color = "orange";

                if(rsi < 30){
                    signal = "BUY";
                    cls = "buy";
                    color = "blue";
                }
                else if(rsi > 70){
                    signal = "SELL";
                    cls = "sell";
                    color = "red";
                }

                let trend = rsi < 50 ? "DOWNTREND" : "UPTREND";
                let confidence = (rsi < 30 || rsi > 70) ? "HIGH" : "LOW";

                html += `
                <div class="card ${cls}">
                    <b>${pair}</b><br>

                    <span class="badge ${color}">
                        ${signal}
                    </span>

                    <small>RSI: ${rsi}</small>
                    <small>Trend: ${trend}</small>
                    <small>Confidence: ${confidence}</small>
                </div>`;
            });

            document.getElementById("signals").innerHTML = html;
        }
        </script>

    </body>
    </html>
    '''

if __name__ == "__main__":
    app.run()
