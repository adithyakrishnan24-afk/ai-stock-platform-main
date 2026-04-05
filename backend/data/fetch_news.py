import requests
from config import FINNHUB_API_KEY
from datetime import datetime, timedelta


def fetch_news(symbol: str):

    if not FINNHUB_API_KEY:
        return {"sentiment": 0.0, "headlines": []}

    symbol = symbol.upper()

    # Index proxies
    if symbol == "^NSEI":
        symbol = "NIFTYBEES"
    elif symbol == "^BSESN":
        symbol = "SENSEXBEES"
    elif symbol == "^GSPC":
        symbol = "SPY"

    # Commodities → no direct news
    elif symbol in ["GC=F", "SI=F", "CL=F"]:
        return {"sentiment": 0.0, "headlines": []}

    # Remove .NS for finnhub
    symbol = symbol.replace(".NS", "")

    today = datetime.utcnow()
    past = today - timedelta(days=30)

    url = "https://finnhub.io/api/v1/company-news"

    params = {
        "symbol": symbol,
        "from": past.strftime("%Y-%m-%d"),
        "to": today.strftime("%Y-%m-%d"),
        "token": FINNHUB_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except Exception:
        return {"sentiment": 0.0, "headlines": []}

    headlines = [
        item["headline"]
        for item in data
        if isinstance(item, dict) and item.get("headline")
    ]

    return {
        "sentiment": 0.0,
        "headlines": headlines
    }