from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from data.fetch_prices import get_stock_data
from data.fetch_news import fetch_news
from sentiment.sentiment_analyzer import analyze_sentiment
from ml.random_forest import predict_trend
from ml.risk_analyzer import calculate_risk
from trading.paper_trading import execute_trade, get_portfolio_summary
from chatbot.advisor_bot import chatbot_reply

app = FastAPI(title="AI Stock Investment Platform API")

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {
        "status": "running",
        "api": "AI Stock Investment Platform"
    }

# =========================
# STOCK ANALYSIS (RISK-AWARE ENGINE)
# =========================
@app.get("/analyze/{symbol}")
def analyze(symbol: str):

    symbol = symbol.upper()

    # ---------- FETCH PRICE DATA ----------
    try:
        prices = get_stock_data(symbol)
    except:
        prices = []

    if not prices or len(prices) < 20:
        return {
            "symbol": symbol,
            "signal": "HOLD",
            "prediction": 0,
            "sentiment": 0,
            "confidence": 0,
            "buy_score": 50,
            "risk_level": "Unknown",
            "model_mae": 0
        }

    # ---------- PREDICTION ----------
    try:
        prediction, mae = predict_trend(prices)
    except:
        prediction, mae = 0, 0

    # ---------- SENTIMENT ----------
    # ---------- SENTIMENT ----------
    try:

        # If NIFTY index
        if symbol == "^NSEI":
            components = [
                "RELIANCE.NS",
                "HDFCBANK.NS",
                "INFY.NS",
                "TCS.NS",
                "ICICIBANK.NS"
            ]
            values = [analyze_sentiment(s) for s in components]
            sentiment = sum(values) / len(values)

        # If SENSEX index
        elif symbol == "^BSESN":
            components = [
                "RELIANCE.NS",
                "HDFCBANK.NS",
                "INFY.NS"
            ]
            values = [analyze_sentiment(s) for s in components]
            sentiment = sum(values) / len(values)

        # Normal stocks / crypto
        else:
            sentiment = analyze_sentiment(symbol)

    except:
        sentiment = 0
        
    # ---------- RISK ----------
    try:
        risk = calculate_risk(prices)
    except:
        risk = "Unknown"

    # ==========================================
    # 🔥 RISK-AWARE SIGNAL LOGIC
    # ==========================================

    non_equity_assets = [
        "GC=F", "SI=F", "CL=F",
        "BTC-USD", "ETH-USD"
    ]

    # Index / Commodity / Crypto
    if symbol.startswith("^") or symbol in non_equity_assets:

        if prediction > 0.003:
            signal = "BUY"
        elif prediction < -0.003:
            signal = "SELL"
        else:
            signal = "HOLD"

    # Stocks (Risk-adjusted)
    else:

        if prediction > 0.005 and sentiment > 0:

            if risk == "High":
                signal = "SPECULATIVE BUY"
            else:
                signal = "BUY"

        elif prediction < -0.005 and sentiment < 0:

            if risk == "High":
                signal = "SPECULATIVE SELL"
            else:
                signal = "SELL"

        else:
            signal = "HOLD"

    # ---------- BUY SCORE ----------
    buy_score = normalize_buy_score(prediction, sentiment)

    # ---------- CONFIDENCE (Penalty for High Risk) ----------
    confidence = int((abs(prediction) + abs(sentiment)) * 5000)

    if risk == "High":
        confidence = int(confidence * 0.7)

    confidence = min(100, confidence)

    return {
        "symbol": symbol,
        "signal": signal,
        "prediction": round(prediction, 4),
        "sentiment": round(sentiment, 3),
        "confidence": confidence,
        "buy_score": buy_score,
        "risk_level": risk,
        "model_mae": mae
    }

# =========================
# PRICE DATA
# =========================
@app.get("/prices/{symbol}")
def prices(symbol: str):
    symbol = symbol.upper()
    try:
        return get_stock_data(symbol) or []
    except:
        return []

# =========================
# NEWS
# =========================
@app.get("/news/{symbol}")
def news(symbol: str):
    symbol = symbol.upper()
    try:
        return fetch_news(symbol)
    except:
        return {"headlines": [], "sentiment": 0.0}

# =========================
# MARKET NEWS (US MARKET BASED)
# =========================
@app.get("/market-news")
def market_news():
    try:
        return fetch_news("SPY")
    except:
        return {"headlines": []}

# =========================
# GLOBAL MARKET SENTIMENT
# (US + India + Gold + Crypto)
# =========================
@app.get("/market-sentiment")
def market_sentiment():

    symbols = [
        "AAPL", "MSFT", "TSLA", "NVDA",
        "RELIANCE.NS", "HDFCBANK.NS", "INFY.NS",
        "GC=F",
        "BTC-USD"
    ]

    sentiments = []

    for s in symbols:
        try:
            sentiments.append(analyze_sentiment(s))
        except:
            pass

    if not sentiments:
        return {"value": 0, "mood": "Unavailable"}

    avg = sum(sentiments) / len(sentiments)

    if avg > 0.05:
        mood = "Bullish 📈"
    elif avg < -0.05:
        mood = "Bearish 📉"
    else:
        mood = "Neutral ⚖️"

    return {
        "value": round(avg, 3),
        "mood": mood
    }

# =========================
# PAPER TRADING
# =========================
@app.post("/trade")
def trade(order: Dict):
    return execute_trade(order)

@app.get("/portfolio")
def portfolio():
    return get_portfolio_summary()

# =========================
# CHATBOT
# =========================
@app.post("/chat")
def chat(data: Dict):
    message = data.get("message", "")
    if not message:
        return {"reply": "Please provide a message."}

    return {"reply": chatbot_reply(message)}

# =========================
# BUY SCORE NORMALIZATION
# =========================
def normalize_buy_score(prediction: float, sentiment: float) -> int:
    score = (prediction * 0.7) + (sentiment * 0.3)
    score = max(-0.05, min(0.05, score))
    normalized = int(((score + 0.05) / 0.10) * 100)
    return normalized