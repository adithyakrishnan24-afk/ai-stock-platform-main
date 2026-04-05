from sentiment.sentiment_analyzer import analyze_sentiment
from ml.random_forest import predict_trend
from data.fetch_prices import get_stock_data

def chatbot_reply(message: str) -> str:

    message = message.lower().strip()

    # ---------------------------------------------------
    # STOCK EDUCATION
    # ---------------------------------------------------

    if "what is stock" in message or "what are stocks" in message:
        return (
            "A stock represents partial ownership in a company. "
            "When you buy a stock, you own a small portion of that company. "
            "Stock prices change based on company performance, investor sentiment, "
            "market conditions, earnings reports, and macroeconomic factors."
        )

    if "what is sentiment" in message:
        return (
            "Market sentiment measures how investors feel about a stock. "
            "Positive sentiment suggests optimism (bullish), "
            "while negative sentiment suggests fear (bearish). "
            "We calculate sentiment using VADER NLP on financial news headlines."
        )

    # ---------------------------------------------------
    # COMPARISON LOGIC
    # ---------------------------------------------------

    if "compare" in message:

        words = message.upper().split()
        symbols = [w for w in words if w.isalpha() and len(w) <= 6]

        if len(symbols) < 2:
            return "Please specify two stock symbols to compare. Example: Compare AAPL and MSFT"

        s1, s2 = symbols[0], symbols[1]

        return compare_stocks(s1, s2)

    # ---------------------------------------------------
    # BUY / SELL / HOLD QUESTIONS
    # ---------------------------------------------------

    if "buy" in message or "sell" in message or "hold" in message:

        words = message.upper().split()
        symbols = [w for w in words if w.isalpha() and len(w) <= 7]

        if not symbols:
            return "Please specify a stock symbol. Example: Should I buy AAPL?"

        symbol = symbols[-1]

        return analyze_stock(symbol)

    # ---------------------------------------------------
    # WHICH STOCK IS BETTER
    # ---------------------------------------------------

    if "which" in message and "better" in message:
        words = message.upper().split()
        symbols = [w for w in words if w.isalpha() and len(w) <= 6]

        if len(symbols) >= 2:
            return compare_stocks(symbols[0], symbols[1])

    # ---------------------------------------------------
    # DEFAULT FALLBACK
    # ---------------------------------------------------

    return (
        "You can ask me things like:\n"
        "- Should I buy AAPL?\n"
        "- Compare TSLA and NVDA\n"
        "- Which is better MSFT or GOOGL?\n"
        "- What is market sentiment?\n"
        "- Explain volatility risk"
    )


# ========================================================
# HELPER: ANALYZE ONE STOCK
# ========================================================

def analyze_stock(symbol: str):

    prices = get_stock_data(symbol)

    if not prices or len(prices) < 20:
        return f"I don't have enough data to analyze {symbol}."

    prediction, _ = predict_trend(prices)
    sentiment = analyze_sentiment(symbol)

    signal = "HOLD"

    if prediction > 0.005 and sentiment > 0:
        signal = "BUY"
    elif prediction < -0.005 and sentiment < 0:
        signal = "SELL"

    explanation = (
        f"Stock: {symbol}\n\n"
        f"Prediction Trend: {round(prediction*100,2)}%\n"
        f"Sentiment Score: {sentiment}\n\n"
        f"Recommendation: {signal}\n\n"
    )

    if signal == "BUY":
        explanation += (
            "The model predicts upward price movement combined "
            "with positive market sentiment. This indicates bullish momentum."
        )
    elif signal == "SELL":
        explanation += (
            "The model predicts downside movement and sentiment "
            "is negative. This suggests bearish pressure."
        )
    else:
        explanation += (
            "The indicators are mixed or neutral. It may be better "
            "to wait for clearer signals."
        )

    return explanation


# ========================================================
# HELPER: COMPARE TWO STOCKS
# ========================================================

def compare_stocks(s1: str, s2: str):

    p1 = get_stock_data(s1)
    p2 = get_stock_data(s2)

    if not p1 or not p2:
        return "Unable to fetch data for comparison."

    pred1, _ = predict_trend(p1)
    pred2, _ = predict_trend(p2)

    sent1 = analyze_sentiment(s1)
    sent2 = analyze_sentiment(s2)

    score1 = pred1 + sent1
    score2 = pred2 + sent2

    better = s1 if score1 > score2 else s2

    return (
        f"Comparison: {s1} vs {s2}\n\n"
        f"{s1} → Trend: {round(pred1*100,2)}%, Sentiment: {sent1}\n"
        f"{s2} → Trend: {round(pred2*100,2)}%, Sentiment: {sent2}\n\n"
        f"Overall, {better} currently shows stronger combined "
        f"technical momentum and sentiment."
    )