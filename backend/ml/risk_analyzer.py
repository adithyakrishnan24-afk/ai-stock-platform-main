import pandas as pd


def calculate_risk(price_data):
    if not price_data or len(price_data) < 10:
        return "Unknown"

    df = pd.DataFrame(price_data)
    df["returns"] = df["Close"].pct_change()

    volatility = df["returns"].std()

    if volatility < 0.01:
        return "Low"
    elif volatility < 0.03:
        return "Medium"
    else:
        return "High"