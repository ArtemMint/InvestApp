import yfinance as yf
from fastapi import APIRouter, Query
from app.utils.helpers import log_request

router = APIRouter()

@log_request
@router.get("/", status_code=200)
async def get_stock_data(
    stock_ticker: str = Query(default="GOOG", description="Stock ticker symbol"),
    period: str = Query(default="1mo", description="Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, etc.)"),
    interval: str = Query(default="1h", description="Data interval (1m, 5m, 15m, 1h, 1d, etc.)")
):
    """
    Get stock data with OHLCV (Open, High, Low, Close, Volume) for candlestick charts
    :return

    """
    try:
        # Download stock data
        data = yf.download(stock_ticker, period=period, interval=interval, progress=False)

        if data.empty:
            return {"error": "No data found for the given ticker", "data": []}

        # Convert to list of candlestick data
        candlesticks = []
        for timestamp, row in data.iterrows():
            candlesticks.append({
                "time": timestamp.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })

        return {
            "ticker": stock_ticker,
            "period": period,
            "interval": interval,
            "data": candlesticks
        }
    except Exception as e:
        return {"error": str(e), "data": []}

@log_request
@router.get("/recommendations", status_code=200)
async def get_recommendations(stock_ticker: str = Query(default="", description="Stock ticker symbol")):
    """
    Get recommendations for ticker.
    :param stock_ticker: For example: GOOG
    :return: JSON {'period': '0m', 'strongBuy': 12, 'buy': 48, 'hold': 8, 'sell': 0, 'strongSell': 0}
    """
    recommendations_json = yf.Ticker(stock_ticker).get_recommendations(as_dict=True)
    latest_recommendations = {key: values[0] for key, values in recommendations_json.items()}
    return latest_recommendations

@log_request
@router.get("/price_target", status_code=200)
async def get_price_target(stock_ticker: str = Query(default="", description="Stock ticker symbol")):
    """
    Get price target for ticker.
    :param stock_ticker:
    :return: JSON {'current': 304.82, 'high': 405.0, 'low': 185.0, 'mean': 359.2353, 'median': 375.0}
    """
    price_target = yf.Ticker(stock_ticker).get_analyst_price_targets()
    return price_target

@log_request
@router.get("/earnings_history", status_code=200)
async def get_earnings(stock_ticker: str = Query(default="", description="Stock ticker symbol")):
    """
    Get earnings for ticker.
    :param stock_ticker:
    :return:
    {'epsActual': {Timestamp('2025-03-31 00:00:00'): 2.81, Timestamp('2025-06-30 00:00:00'): 2.31, Timestamp('2025-09-30 00:00:00'): 2.87, Timestamp('2025-12-31 00:00:00'): 2.82}, 'epsEstimate': {Timestamp('2025-03-31 00:00:00'): 2.00951, Timestamp('2025-06-30 00:00:00'): 2.19807, Timestamp('2025-09-30 00:00:00'): 2.26206, Timestamp('2025-12-31 00:00:00'): 2.64089}, 'epsDifference': {Timestamp('2025-03-31 00:00:00'): 0.8, Timestamp('2025-06-30 00:00:00'): 0.11, Timestamp('2025-09-30 00:00:00'): 0.61, Timestamp('2025-12-31 00:00:00'): 0.18}, 'surprisePercent': {Timestamp('2025-03-31 00:00:00'): 0.3984, Timestamp('2025-06-30 00:00:00'): 0.0509, Timestamp('2025-09-30 00:00:00'): 0.2688, Timestamp('2025-12-31 00:00:00'): 0.0678}}
    """
    earnings_history = yf.Ticker(stock_ticker).get_earnings_history(as_dict=True)
    return earnings_history
