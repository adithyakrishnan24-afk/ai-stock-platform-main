from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from data.fetch_news import fetch_news

analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(symbol: str) -> float:
    """
    Returns sentiment score between -1 and +1.

    Handles:
    - Indices
    - Commodities
    - Crypto

    Combines VADER + API sentiment.
    """

    try:
        symbol = symbol.upper()

        # ===============================
        # ASSET CLASS FILTERING
        # ===============================

        non_equity_assets = [
            "GC=F",    # Gold
            "SI=F",    # Silver
            "CL=F",    # Crude Oil
            "BTC-USD", # Bitcoin
            "ETH-USD"  # Ethereum
        ]

        # Indices (start with ^) OR non-equity assets → neutral baseline
        if symbol.startswith("^") or symbol in non_equity_assets:
            return 0.0

        # ===============================
        # FETCH NEWS
        # ===============================
        news_data = fetch_news(symbol)

        headlines = news_data.get("headlines", [])
        api_sentiment = float(news_data.get("sentiment", 0.0))

        if not headlines:
            return 0.0

        # ===============================
        # VADER ANALYSIS
        # ===============================
        vader_scores = []

        for text in headlines:
            score = analyzer.polarity_scores(text)["compound"]

            # Ignore weak neutral noise
            if abs(score) >= 0.05:
                vader_scores.append(score)

        if not vader_scores:
            return 0.0

        vader_avg = sum(vader_scores) / len(vader_scores)

        # Since Finnhub sentiment is placeholder 0,
        # give more weight to VADER
        combined = (vader_avg * 0.80) + (api_sentiment * 0.20)

        # Clamp safely
        combined = max(-1.0, min(1.0, combined))

        return round(combined, 3)

    except Exception:
        return 0.0