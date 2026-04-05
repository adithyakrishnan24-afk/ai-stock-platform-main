const API_BASE = "https://ai-stock-platform-zpkg.onrender.com";

/* ===========================================
   MASTER ASSET LIST (ALL MARKETS)
=========================================== */
const DEFAULT_STOCKS = [
  // 🇺🇸 US
  "AAPL",
  "MSFT",
  "NVDA",
  "TSLA",

  // 🇮🇳 India
  "RELIANCE.NS",
  "HDFCBANK.NS",
  "INFY.NS",

  // 📊 Index
  "^NSEI",

  // 🥇 Gold
  "GC=F",

  // 🪙 Crypto
  "BTC-USD"
];

let expandedChartInstance = null;

/* =====================================================
   SYMBOL NORMALIZATION (Friendly → Yahoo Format)
===================================================== */
function normalizeSymbol(symbol) {

  const map = {

    // 📊 Indices
    "SENSEX": "^BSESN",
    "BSESN": "^BSESN",
    "NIFTY": "^NSEI",
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",

    // 🥇 Commodities
    "GOLD": "GC=F",
    "SILVER": "SI=F",
    "CRUDE": "CL=F",
    "CRUDE OIL": "CL=F",
    "OIL": "CL=F",

    // 🪙 Crypto
    "BITCOIN": "BTC-USD",
    "BTC": "BTC-USD",
    "ETHEREUM": "ETH-USD",
    "ETH": "ETH-USD"
  };

  return map[symbol] || symbol;
}

/* =====================================================
   LOGO + SYMBOL FORMAT
===================================================== */
function getLogo(sym) {

  const logoMap = {

    // 🇺🇸 US
    AAPL: "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/apple.svg",
    MSFT: "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/microsoft.svg",
    TSLA: "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/tesla.svg",
    NVDA: "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/nvidia.svg",
    AMZN: "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/amazon.svg",
    GOOGL: "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/google.svg",

    // 🇮🇳 India
    RELIANCE: "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/relianceindustrieslimited.svg",
    TCS: "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/tata.svg",
    HDFCBANK: "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/hdfcbank.svg",
    INFY: "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/infosys.svg",
    ICICIBANK: "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/icicibank.svg",
    ADANIENT: "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/adani.svg",

    // 🥇 Commodities
    "GC=F": "https://img.icons8.com/color/48/gold-bars.png",
    "SI=F": "https://img.icons8.com/color/48/silver-bars.png",
    "CL=F": "https://img.icons8.com/color/48/oil-industry.png",

    // 🪙 Crypto
    "BTC-USD": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/bitcoin.svg",
    "ETH-USD": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/ethereum.svg",

    // 📊 Indices
    "^NSEI": "https://cdn-icons-png.flaticon.com/512/2991/2991148.png",
    "^BSESN": "https://cdn-icons-png.flaticon.com/512/2991/2991148.png",
    "^NSEBANK": "https://cdn-icons-png.flaticon.com/512/2991/2991148.png"
  };

  const clean = sym.replace(".NS", "");
  return logoMap[clean] ||
    "https://cdn-icons-png.flaticon.com/512/2991/2991148.png";
}


/* =====================================================
   FRIENDLY NAME FORMAT
===================================================== */
function formatSymbol(sym) {

  const map = {
    "^BSESN": "SENSEX",
    "^NSEI": "NIFTY 50",
    "^NSEBANK": "BANK NIFTY",
    "GC=F": "GOLD",
    "SI=F": "SILVER",
    "CL=F": "CRUDE OIL",
    "BTC-USD": "BITCOIN",
    "ETH-USD": "ETHEREUM"
  };

  return map[sym] || sym.replace(".NS", "");
}


function safeId(sym) {
  return sym.replace(/[^a-zA-Z0-9]/g, "");
}


/* =====================================================
   ON LOAD
===================================================== */
document.addEventListener("DOMContentLoaded", () => {
  loadDefaultStocks();
  loadMarketSentiment();
  loadMarketNews();
});


/* =====================================================
   LOAD MARKET GRID
===================================================== */
async function loadDefaultStocks() {

  const container = document.getElementById("default-stocks");
  container.innerHTML = "";

  for (const sym of DEFAULT_STOCKS) {

    const id = safeId(sym);

    const card = document.createElement("div");
    card.className = "stock-card";
    card.onclick = () => expandChart(sym);

    card.innerHTML = `
      <div class="card-header">
        <img src="${getLogo(sym)}"
             class="stock-logo"
             onerror="this.src='https://cdn-icons-png.flaticon.com/512/2991/2991148.png'"/>
        <h3>${formatSymbol(sym)}</h3>
      </div>

      <div class="mini-chart">
        <canvas id="chart-${id}"></canvas>
      </div>

      <div class="expanded-info">
        <p class="news">Loading latest news...</p>
      </div>

      <p class="mini-signal loading">Loading...</p>
    `;

    container.appendChild(card);

    renderMiniChart(`chart-${id}`, sym);

    /* ---------- LOAD SIGNAL ---------- */
    fetch(`${API_BASE}/analyze/${sym}`)
      .then(res => res.json())
      .then(data => {
        const signalEl = card.querySelector(".mini-signal");
        signalEl.textContent = data.signal || "HOLD";
        signalEl.className = "mini-signal " + (data.signal || "HOLD");
      })
      .catch(() => {
        const signalEl = card.querySelector(".mini-signal");
        signalEl.textContent = "HOLD";
        signalEl.className = "mini-signal HOLD";
      });

    /* ---------- LOAD NEWS ---------- */
    fetch(`${API_BASE}/news/${sym}`)
      .then(res => res.json())
      .then(news => {
        const newsEl = card.querySelector(".news");

        if (!news.headlines || news.headlines.length === 0) {
          newsEl.textContent = "No major news.";
          return;
        }

        newsEl.innerHTML = news.headlines
          .slice(0, 2)
          .map(h => `• ${h}`)
          .join("<br>");
      })
      .catch(() => {
        card.querySelector(".news").textContent = "News unavailable";
      });
  }
}


/* =====================================================
   MARKET SENTIMENT
===================================================== */
async function loadMarketSentiment() {
  const el = document.getElementById("market-sentiment");

  try {
    const res = await fetch(`${API_BASE}/market-sentiment`);
    const data = await res.json();
    el.textContent = `${data.mood} (${data.value})`;
  } catch {
    el.textContent = "Unavailable";
  }
}


/* =====================================================
   MARKET NEWS
===================================================== */
async function loadMarketNews() {
  const container = document.getElementById("market-news");

  try {
    const res = await fetch(`${API_BASE}/market-news`);
    const data = await res.json();

    if (!data.headlines || data.headlines.length === 0) {
      container.textContent = "No major market news.";
      return;
    }

    container.innerHTML = data.headlines
      .slice(0, 5)
      .map(h => `<div class="news-item">• ${h}</div>`)
      .join("");

  } catch {
    container.textContent = "News unavailable.";
  }
}


/* =====================================================
   MINI CHART
===================================================== */
async function renderMiniChart(canvasId, symbol) {

  try {
    const res = await fetch(`${API_BASE}/prices/${symbol}`);
    const rawData = await res.json();
    const data = rawData.filter(p => p.Close && p.Close > 0);

    const ctx = document.getElementById(canvasId).getContext("2d");

    new Chart(ctx, {
      type: "line",
      data: {
        labels: data.map(p => p.date),
        datasets: [{
          data: data.map(p => p.Close),
          borderColor: "#22c55e",
          borderWidth: 2,
          tension: 0.35,
          pointRadius: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { display: false } }
      }
    });

  } catch (err) {
    console.log("Mini chart error:", err);
  }
}


/* =====================================================
   EXPANDED CHART
===================================================== */
async function expandChart(symbol) {

  const modal = document.getElementById("chart-modal");
  modal.classList.add("active");

  try {
    const res = await fetch(`${API_BASE}/prices/${symbol}`);
    const rawData = await res.json();
    const data = rawData.filter(p => p.Close && p.Close > 0);

    const ctx = document.getElementById("expanded-chart").getContext("2d");

    if (expandedChartInstance) expandedChartInstance.destroy();

    expandedChartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: data.map(p => p.date),
        datasets: [{
          label: `${formatSymbol(symbol)} Price`,
          data: data.map(p => p.Close),
          borderColor: "#22c55e",
          borderWidth: 2,
          tension: 0.25,
          pointRadius: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { labels: { color: "#e5e7eb" } }
        },
        scales: {
          x: { ticks: { color: "#94a3b8" } },
          y: { ticks: { color: "#94a3b8" } }
        }
      }
    });

  } catch (err) {
    console.log("Expanded chart error:", err);
  }
}

function closeModal() {
  document.getElementById("chart-modal").classList.remove("active");
}

/* =====================================================
   SEARCH ANALYSIS FUNCTION
===================================================== */
async function analyzeStock() {

  const symbolInput = document.getElementById("symbol");
  const output = document.getElementById("output");

  if (!symbolInput || !output) {
    console.log("Missing input or output element");
    return;
  }

  let symbol = symbolInput.value.trim().toUpperCase();
  symbol = normalizeSymbol(symbol);

  if (!symbol) {
    output.innerHTML = "Please enter a symbol.";
    return;
  }

  output.innerHTML = "Analyzing...";

  try {
    const res = await fetch(`${API_BASE}/analyze/${symbol}`);

    if (!res.ok) {
      throw new Error("API Error");
    }

    const data = await res.json();

    let recommendation =
      data.buy_score >= 75 ? "STRONG BUY" :
      data.buy_score >= 60 ? "BUY" :
      data.buy_score >= 45 ? "HOLD" : "SELL";

    output.innerHTML = `
      <h3>${symbol}</h3>
      <p><b>Prediction:</b> ${data.prediction}</p>
      <p><b>Sentiment:</b> ${data.sentiment}</p>
      <p><b>Risk Level:</b> ${data.risk_level}</p>
      <p><b>Model MAE:</b> ${data.model_mae}</p>
      <p><b>Buy Score:</b> ${data.buy_score}</p>
      <h2 style="margin-top:15px;">${recommendation}</h2>
    `;

    if (typeof renderMeter === "function") {
      renderMeter(data.buy_score);
    }

  } catch (err) {
    console.log("Analyze Error:", err);
    output.innerHTML = "Error fetching data.";
  }
}