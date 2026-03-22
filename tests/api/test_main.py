"""
Tests for the main API endpoints that are not part of specific submodules.
These are mostly static file serving and health check endpoints.
"""
import pytest


class TestMainAPI:
    """Tests for the main API endpoints that are not part of specific submodules."""

    @pytest.mark.main_api
    def test_get_health(self, client):
        """The /health endpoint should return 200 with a JSON body indicating the API is running."""
        response = client.get(f"/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["message"] == "API is running"

    @pytest.mark.main_api
    def test_get_index(self, client):
        """The root / endpoint should return 200 and serve the index.html file."""
        response = client.get("/")
        assert response.status_code == 200

    @pytest.mark.main_api
    def test_get_stock(self, client):
        """The /stock endpoint should return 200 and serve the stock.html file."""
        response = client.get("/stock")
        assert response.status_code == 200

    @pytest.mark.main_api
    def test_get_invest_planing(self, client):
        """The /investment_calc endpoint should return 200 and serve the investment_calc.html file."""
        response = client.get("/investment_calc")
        assert response.status_code == 200

    @pytest.mark.main_api
    def test_get_portfolio_html(self, client):
        """The /portfolio endpoint should return 200 and serve the portfolio.html file."""
        response = client.get("/portfolio")
        assert response.status_code == 200
