const API_BASE = "https://ai-stock-platform-zpkg.onrender.com";

async function placeTrade(type) {
  const symbol = document.getElementById("tradeSymbol").value.toUpperCase();
  const qty = parseInt(document.getElementById("quantity").value);
  const price = parseFloat(document.getElementById("price").value);
  const result = document.getElementById("tradeResult");

  if (!symbol || !qty || !price) {
    result.innerHTML = "⚠️ Fill all fields";
    return;
  }

  result.innerHTML = "⏳ Placing trade...";

  const order = { symbol, quantity: qty, price, type };

  try {
    const res = await fetch(`${API_BASE}/trade`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(order)
    });

    if (!res.ok) throw new Error("Trade failed");

    const data = await res.json();

    result.innerHTML = `
      <div class="trade-success">
        <b>✅ Trade Executed</b>
        <pre>${JSON.stringify(data, null, 2)}</pre>
      </div>
    `;

  } catch (err) {
    result.innerHTML = "❌ Trade failed. Backend not reachable.";
  }
}

