import numpy as np
import pandas as pd
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
    Get stock data with OHLCV (Open, High, Low, Close, Volume, MA200, MA50, MA20, MA9)
    for a given stock ticker, period, and interval.
    :param stock_ticker: For example: GOOG
    :param period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, etc.)
    :param interval: Data interval (1m, 5m, 15m, 1h, 1d, etc.)

    :return
        {
        "ticker": "GOOG",
        "period": "3mo",
        "interval": "1h",
        "data": [
            {
                "time": "2025-01-01T00:00:00Z",
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 105.0,
                "volume": 1000000,
                "ma200": 102.5,
                "ma50": 104.0,
                "ma20": 103.0,
                "ma9": 105.0
            },
            ...
        ]
        }
    """
    try:
        # Download stock data using yfinance
        data = yf.download(stock_ticker, period=period, interval=interval, progress=False)

        if data.empty:
            return {"error": "No data found for the given ticker", "data": []}

        # If the columns are a MultiIndex (which can happen with some yfinance data), we need to flatten it
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        # Compute moving averages
        close_data = data["Close"]
        data["ma200"] = close_data.rolling(window=200).mean()
        data["ma50"] = close_data.rolling(window=50).mean()
        data["ma20"] = close_data.rolling(window=20).mean()
        data["ma9"] = close_data.rolling(window=9).mean()

        # Renaming columns to match the expected output format
        data = data.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })

        # Add time column from index
        data["time"] = data.index.map(lambda x: x.isoformat())

        # Take only the necessary columns and ensure they are in the correct order
        cols = ["time", "open", "high", "low", "close", "volume", "ma200", "ma50", "ma20", "ma9"]
        data = data[cols]

        # Check for NaN values and replace them with None for JSON serialization
        data = data.replace({np.nan: None})

        # Convert DataFrame to list of dictionaries for JSON response
        candlesticks = data.to_dict(orient="records")

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
