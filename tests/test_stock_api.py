#!/usr/bin/env python3
"""
Tests for stock API endpoints: /api/v1/stock/
Uses unittest.mock to patch yfinance so tests run without network access.
"""
from unittest.mock import patch, MagicMock
import pandas as pd

STOCK_API = "/api/v1/stock"


# ---------------------------------------------------------------------------
# Helpers – build fake yfinance responses
# ---------------------------------------------------------------------------

def _make_ohlcv_dataframe(rows: int = 3) -> pd.DataFrame:
    """Return a minimal OHLCV DataFrame that mimics yfinance.download output."""
    dates = pd.date_range("2026-01-01", periods=rows, freq="h")
    data = {
        "Open": [100.0 + i for i in range(rows)],
        "High": [105.0 + i for i in range(rows)],
        "Low": [95.0 + i for i in range(rows)],
        "Close": [102.0 + i for i in range(rows)],
        "Volume": [1_000_000 + i * 100 for i in range(rows)],
    }
    return pd.DataFrame(data, index=dates)


# ---------------------------------------------------------------------------
# GET /api/v1/stock/  –  Stock OHLCV data
# ---------------------------------------------------------------------------

class TestGetStockData:
    """Tests for the GET /api/v1/stock/ endpoint."""

    @patch("app.api.v1.endpoints.stock.yf.download")
    def test_default_params_returns_200(self, mock_download, client):
        """Default request should return 200 with ticker, period, interval, and data."""
        mock_download.return_value = _make_ohlcv_dataframe()

        response = client.get(f"{STOCK_API}/")

        assert response.status_code == 200
        body = response.json()
        assert body["ticker"] == "GOOG"
        assert body["period"] == "1mo"
        assert body["interval"] == "1h"
        assert isinstance(body["data"], list)
        assert len(body["data"]) == 3

    @patch("app.api.v1.endpoints.stock.yf.download")
    def test_custom_params(self, mock_download, client):
        """Custom query parameters should be forwarded correctly."""
        mock_download.return_value = _make_ohlcv_dataframe(5)

        response = client.get(
            f"{STOCK_API}/",
            params={"stock_ticker": "MSFT", "period": "5d", "interval": "1d"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["ticker"] == "MSFT"
        assert body["period"] == "5d"
        assert body["interval"] == "1d"
        assert len(body["data"]) == 5

        # Verify yfinance was called with the right arguments
        mock_download.assert_called_once_with(
            "MSFT", period="5d", interval="1d", progress=False,
        )

    @patch("app.api.v1.endpoints.stock.yf.download")
    def test_candlestick_data_structure(self, mock_download, client):
        """Each data point must contain time, OHLC, and volume fields."""
        mock_download.return_value = _make_ohlcv_dataframe(1)

        response = client.get(f"{STOCK_API}/")
        body = response.json()
        point = body["data"][0]

        expected_keys = {"time", "open", "high", "low", "close", "volume"}
        assert expected_keys == set(point.keys())
        assert isinstance(point["open"], float)
        assert isinstance(point["volume"], int)

    @patch("app.api.v1.endpoints.stock.yf.download")
    def test_empty_dataframe_returns_error(self, mock_download, client):
        """An empty DataFrame (invalid ticker) should return an error message."""
        mock_download.return_value = pd.DataFrame()

        response = client.get(
            f"{STOCK_API}/",
            params={"stock_ticker": "INVALID123"},
        )

        assert response.status_code == 200
        body = response.json()
        assert "error" in body
        assert body["data"] == []

    @patch("app.api.v1.endpoints.stock.yf.download")
    def test_yfinance_exception_returns_error(self, mock_download, client):
        """If yfinance raises, endpoint should catch and return an error payload."""
        mock_download.side_effect = Exception("Network error")

        response = client.get(f"{STOCK_API}/")

        assert response.status_code == 200
        body = response.json()
        assert "error" in body
        assert "Network error" in body["error"]
        assert body["data"] == []


# ---------------------------------------------------------------------------
# GET /api/v1/stock/recommendations
# ---------------------------------------------------------------------------

class TestGetRecommendations:
    """Tests for the GET /api/v1/stock/recommendations endpoint."""

    @patch("app.api.v1.endpoints.stock.yf.Ticker")
    def test_recommendations_returns_200(self, mock_ticker_cls, client):
        mock_ticker = MagicMock()
        mock_ticker.get_recommendations.return_value = {
            "period": ["0m"],
            "strongBuy": [12],
            "buy": [48],
            "hold": [8],
            "sell": [0],
            "strongSell": [0],
        }
        mock_ticker_cls.return_value = mock_ticker

        response = client.get(
            f"{STOCK_API}/recommendations",
            params={"stock_ticker": "GOOG"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["strongBuy"] == 12
        assert body["buy"] == 48

    @patch("app.api.v1.endpoints.stock.yf.Ticker")
    def test_recommendations_data_structure(self, mock_ticker_cls, client):
        expected_keys = {"period", "strongBuy", "buy", "hold", "sell", "strongSell"}
        mock_ticker = MagicMock()
        mock_ticker.get_recommendations.return_value = {
            k: [0] for k in expected_keys
        }
        mock_ticker_cls.return_value = mock_ticker

        response = client.get(
            f"{STOCK_API}/recommendations",
            params={"stock_ticker": "AAPL"},
        )

        assert response.status_code == 200
        assert expected_keys == set(response.json().keys())


# ---------------------------------------------------------------------------
# GET /api/v1/stock/price_target
# ---------------------------------------------------------------------------

class TestGetPriceTarget:
    """Tests for the GET /api/v1/stock/price_target endpoint."""

    @patch("app.api.v1.endpoints.stock.yf.Ticker")
    def test_price_target_returns_200(self, mock_ticker_cls, client):
        mock_ticker = MagicMock()
        mock_ticker.get_analyst_price_targets.return_value = {
            "current": 304.82,
            "high": 405.0,
            "low": 185.0,
            "mean": 359.24,
            "median": 375.0,
        }
        mock_ticker_cls.return_value = mock_ticker

        response = client.get(
            f"{STOCK_API}/price_target",
            params={"stock_ticker": "GOOG"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["current"] == 304.82
        assert body["high"] == 405.0

    @patch("app.api.v1.endpoints.stock.yf.Ticker")
    def test_price_target_data_structure(self, mock_ticker_cls, client):
        expected_keys = {"current", "high", "low", "mean", "median"}
        mock_ticker = MagicMock()
        mock_ticker.get_analyst_price_targets.return_value = {
            k: 0.0 for k in expected_keys
        }
        mock_ticker_cls.return_value = mock_ticker

        response = client.get(
            f"{STOCK_API}/price_target",
            params={"stock_ticker": "AAPL"},
        )

        assert response.status_code == 200
        assert expected_keys == set(response.json().keys())


# ---------------------------------------------------------------------------
# GET /api/v1/stock/earnings_history
# ---------------------------------------------------------------------------

class TestGetEarningsHistory:
    """Tests for the GET /api/v1/stock/earnings_history endpoint."""

    @patch("app.api.v1.endpoints.stock.yf.Ticker")
    def test_earnings_history_returns_200(self, mock_ticker_cls, client):
        mock_ticker = MagicMock()
        mock_ticker.get_earnings_history.return_value = {
            "epsActual": {"2025-03-31": 2.81},
            "epsEstimate": {"2025-03-31": 2.01},
            "epsDifference": {"2025-03-31": 0.80},
            "surprisePercent": {"2025-03-31": 0.40},
        }
        mock_ticker_cls.return_value = mock_ticker

        response = client.get(
            f"{STOCK_API}/earnings_history",
            params={"stock_ticker": "GOOG"},
        )

        assert response.status_code == 200
        body = response.json()
        assert "epsActual" in body

    @patch("app.api.v1.endpoints.stock.yf.Ticker")
    def test_earnings_history_data_structure(self, mock_ticker_cls, client):
        expected_keys = {"epsActual", "epsEstimate", "epsDifference", "surprisePercent"}
        mock_ticker = MagicMock()
        mock_ticker.get_earnings_history.return_value = {k: {} for k in expected_keys}
        mock_ticker_cls.return_value = mock_ticker

        response = client.get(
            f"{STOCK_API}/earnings_history",
            params={"stock_ticker": "AAPL"},
        )

        assert response.status_code == 200
        assert expected_keys == set(response.json().keys())
