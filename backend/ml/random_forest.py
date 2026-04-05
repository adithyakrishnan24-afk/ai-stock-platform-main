import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from ml.feature_engineering import prepare_features


def predict_trend(price_data):
    if not price_data or len(price_data) < 30:
        return 0.0, 0.0

    try:
        df = prepare_features(price_data)

        features = ["returns", "ma_5", "ma_10", "volatility", "momentum"]

        X = df[features]
        y = df["Close"].shift(-1)

        X = X[:-1]
        y = y[:-1]

        # Train/Test Split (80/20)
        split = int(len(X) * 0.8)

        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=8,
            random_state=42
        )

        model.fit(X_train, y_train)

        # Accuracy Calculation (MAE)
        preds_test = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds_test)

        # Latest Prediction
        latest_features = df[features].iloc[-1:].values
        prediction = model.predict(latest_features)[0]
        current_price = df["Close"].iloc[-1]

        trend = (prediction - current_price) / current_price

        return round(float(trend), 4), round(float(mae), 4)

    except Exception as e:
        print("ML error:", e)
        return 0.0, 0.0