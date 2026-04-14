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
            body { font-family: Arial; text-align: center; padding: 20px; }
            .card {
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                margin: 10px;
            }
            .buy { border-color: blue; }
            .sell { border-color: red; }
            .wait { border-color: orange; }
        </style>
    </head>

    <body>
        <h1>KerrzAI 🤖</h1>

        <button onclick="scan()">Analyze Market</button>

        <div id="signals"></div>

        <script>
        function scan() {
            const pairs = ["Vol 10","Vol 25","Vol 50","Vol 75","Jump 25","Jump 50","Jump 100"];
            let html = "";

            pairs.forEach(pair => {
                let rsi = Math.floor(Math.random()*100);
                let signal = "WAIT";
                let cls = "wait";

                if(rsi < 30){ signal="BUY"; cls="buy"; }
                else if(rsi > 70){ signal="SELL"; cls="sell"; }

                html += `
                <div class="card ${cls}">
                    <b>${pair}</b><br>
                    Signal: ${signal}<br>
                    RSI: ${rsi}
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
