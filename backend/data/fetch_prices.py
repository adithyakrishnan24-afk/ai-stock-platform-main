import yfinance as yf


def get_stock_data(symbol: str, limit: int = 30):
    """
    Fetch recent daily stock data using Yahoo Finance.
    Returns list of candle dictionaries.
    """

    try:
        stock = yf.Ticker(symbol.upper())

        # Get 3 months of data to ensure enough trading days
        df = stock.history(period="3mo")

        if df.empty:
            print("Yahoo returned empty dataframe")
            return []

        # Get last N trading days
        df = df.tail(limit)

        prices = []

        for index, row in df.iterrows():
            prices.append({
                "date": index.strftime("%Y-%m-%d"),
                "Open": float(row["Open"]),
                "High": float(row["High"]),
                "Low": float(row["Low"]),
                "Close": float(row["Close"]),
                "Volume": float(row["Volume"])
            })

        return prices

    except Exception as e:
        print("Yahoo Finance error:", e)
        return []