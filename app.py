async function loadData() {
    try {
        const res = await fetch(`/signal/${currentPair}`);
        const data = await res.json();

        if (data.error) {
            document.getElementById("signal").innerText = "Error loading";
            return;
        }

        document.getElementById("signal").innerText = data.signal;
        document.getElementById("rsi").innerText = "RSI: " + data.rsi;

        //  ADD THESE (fix undefined issue)
        document.getElementById("tradeBox").innerHTML = `
            <h2>${data.pair}</h2>
            <p><b>Trend:</b> ${data.trend}</p>
            <p><b>Signal:</b> ${data.signal}</p>
            <p><b>Entry:</b> ${data.entry}</p>
            <p><b>TP:</b> ${data.tp}</p>
            <p><b>SL:</b> ${data.sl}</p>
            <p><b>BOS:</b> ${data.bos}</p>
            <p><b>Confidence:</b> ${data.confidence}%</p>
        `;

    } catch (err) {
        document.getElementById("signal").innerText = "Server error";
    }
}
