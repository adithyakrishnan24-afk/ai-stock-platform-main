# backend/trading/paper_trading.py

from data.fetch_prices import get_stock_data

# In-memory virtual portfolio (resets on restart)
portfolio = {
    "balance": 100000.0,   # Starting virtual cash
    "holdings": {},        # symbol -> quantity
    "trade_history": []    # list of executed trades
}


def get_live_price(symbol: str) -> float:
    """
    Fetch latest market price using existing price module
    """
    prices = get_stock_data(symbol)
    if not prices:
        return 0.0

    return float(prices[-1]["Close"])


def execute_trade(order: dict):
    """
    Execute paper buy/sell.
    Order format:
    {
        "symbol": "AAPL",
        "action": "buy" | "sell",
        "quantity": 10
    }
    """

    try:
        symbol = order.get("symbol", "").upper()
        action = order.get("action", "").lower()
        quantity = int(order.get("quantity", 0))

        if not symbol or action not in ("buy", "sell") or quantity <= 0:
            return {"status": "error", "message": "Invalid order format"}

        price = get_live_price(symbol)

        if price <= 0:
            return {"status": "error", "message": "Unable to fetch live price"}

        total = round(quantity * price, 2)

        # ================= BUY =================
        if action == "buy":

            if portfolio["balance"] < total:
                return {"status": "error", "message": "Insufficient balance"}

            portfolio["balance"] -= total

            portfolio["holdings"][symbol] = (
                portfolio["holdings"].get(symbol, 0) + quantity
            )

        # ================= SELL =================
        elif action == "sell":

            if portfolio["holdings"].get(symbol, 0) < quantity:
                return {"status": "error", "message": "Insufficient holdings"}

            portfolio["holdings"][symbol] -= quantity
            portfolio["balance"] += total

            # Remove empty holdings
            if portfolio["holdings"][symbol] == 0:
                del portfolio["holdings"][symbol]

        # ================= RECORD TRADE =================
        trade_record = {
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": price,
            "total": total
        }

        portfolio["trade_history"].append(trade_record)

        return {
            "status": "success",
            "message": f"{action.upper()} executed",
            "trade": trade_record,
            "portfolio": get_portfolio_summary()
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_portfolio_summary():
    """
    Calculate total portfolio value including holdings
    """

    total_value = portfolio["balance"]

    holdings_detailed = []

    for symbol, qty in portfolio["holdings"].items():
        price = get_live_price(symbol)
        value = round(qty * price, 2)
        total_value += value

        holdings_detailed.append({
            "symbol": symbol,
            "quantity": qty,
            "current_price": price,
            "value": value
        })

    return {
        "balance": round(portfolio["balance"], 2),
        "holdings": holdings_detailed,
        "total_value": round(total_value, 2),
        "trade_history": portfolio["trade_history"]
    }