import pandas as pd

def prepare_features(price_data):
    df = pd.DataFrame(price_data)

    df["returns"] = df["Close"].pct_change()
    df["ma_5"] = df["Close"].rolling(5).mean()
    df["ma_10"] = df["Close"].rolling(10).mean()
    df["volatility"] = df["returns"].rolling(5).std()
    df["momentum"] = df["Close"] - df["Close"].shift(5)

    df.dropna(inplace=True)

    return df