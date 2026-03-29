import pytest
from fastapi import status

from app.models.asset import AssetType
from tests.utils.assertions import assert_position_in_db, assert_transaction_in_db, \
    assert_transaction_created, assert_position_created

PORTFOLIO_API = "/api/v1/portfolio"


class TestPortfolioAPI:
    """Tests for the Portfolio CRUD endpoints."""

    @pytest.mark.portfolio
    def test_portfolios_returns_200(self, client, persisted_user):
        """Getting the list of portfolios should return 200 with a list body (which may be empty)."""
        response = client.get(f"{PORTFOLIO_API}/")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert isinstance(body, list)
        assert all(item["user_id"] == str(persisted_user.id) for item in body)

    @pytest.mark.portfolio
    def test_portfolios_returns_401_for_unauthenticated_user(self, client):
        """Getting the list of portfolios without authentication should return 401."""
        response = client.get(f"{PORTFOLIO_API}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    @pytest.mark.portfolio
    def test_get_portfolio_by_id_returns_200(self, client, persisted_user, persisted_portfolio):
        """Getting an existing portfolio by ID should return 200 with the portfolio body."""
        response = client.get(f"{PORTFOLIO_API}/{persisted_portfolio.id}")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["name"] == persisted_portfolio.name
        assert body["id"] == str(persisted_portfolio.id)
        assert body["user_id"] == str(persisted_user.id)
        assert body["currency"] == persisted_portfolio.currency
        assert body["is_imported"] == persisted_portfolio.is_imported

    @pytest.mark.portfolio
    def test_get_portfolio_by_id_returns_404(self, client, persisted_user):
        """Getting a non-existing portfolio by ID should return 404."""
        response = client.get(f"{PORTFOLIO_API}/6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Portfolio 6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b not found"

    @pytest.mark.portfolio
    def test_create_portfolio_returns_201(self, client, persisted_user):
        """Creating a portfolio with valid data should return 201 with the created portfolio body."""
        name = "My portfolioResponse"
        currency = "USD"
        payload = {
            "name": name,
            "currency": currency,
        }
        response = client.post(f"{PORTFOLIO_API}/",
                               json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["name"] == name
        assert body["currency"] == currency
        assert body["user_id"] == str(persisted_user.id)
        assert body["is_imported"] is False

    @pytest.mark.portfolio
    def test_create_portfolio_returns_422(self, client, persisted_portfolio):
        """Given invalid portfolio data, should return 422."""
        payload = {
            "name": "",
            "currency": "USD",
        }
        response = client.post(f"{PORTFOLIO_API}/", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.portfolio
    def test_update_portfolio_by_id_returns_200(self, client, persisted_portfolio, persisted_user):
        """Updating an existing portfolio should return 200 with the updated portfolio body."""
        name = "Updated Portfolio"
        currency = "EUR"
        user_id = str(persisted_user.id)
        payload = {
            "name": name,
            "currency": currency,
        }
        response = client.put(f"{PORTFOLIO_API}/{persisted_portfolio.id}", json=payload)
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["name"] == name
        assert body["currency"] == currency
        assert body["user_id"] == str(user_id)
        assert body["id"] == str(persisted_portfolio.id)

    @pytest.mark.portfolio
    def test_update_portfolio_by_id_returns_404(self, client, persisted_portfolio, persisted_user):
        """Updating a non-existing portfolio should return 404."""
        name = "Updated Portfolio"
        currency = "EUR"
        payload = {
            "name": name,
            "currency": currency,
        }
        response = client.put(f"{PORTFOLIO_API}/6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b", json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == f"Portfolio 6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b not found"

    @pytest.mark.portfolio
    def test_delete_portfolio_by_id_returns_204(self, client, persisted_portfolio):
        """Deleting an existing portfolio should return 204 with no content."""
        response = client.delete(f"{PORTFOLIO_API}/{persisted_portfolio.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""

    @pytest.mark.portfolio
    def test_delete_portfolio_by_id_returns_404(self, client, persisted_portfolio):
        """Deleting an existing portfolio should return 204 with no content."""
        response = client.delete(f"{PORTFOLIO_API}/6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Portfolio 6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b not found"

    @pytest.mark.portfolio
    def test_add_position_to_portfolio_return_201(self, client, db_session, persisted_portfolio):
        """Test add position to the portfolio returns 201 and verify it saved to the DB."""
        portfolio_id = persisted_portfolio.id
        ticker = "AAPL"
        quantity = 5
        price_per_share = 250
        payload = {
            "ticker": ticker,
            "quantity": quantity,
            "price_per_share": price_per_share
        }
        response = client.post(f"{PORTFOLIO_API}/{portfolio_id}/position",
                               json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message"] == f"Asset {ticker} added to the portfolio {portfolio_id}."

        assert_position_in_db(db_session, portfolio_id, ticker, quantity, price_per_share)

        assert_transaction_in_db(db_session, portfolio_id, quantity)

    @pytest.mark.portfolio
    def test_add_position_to_portfolio_return_404(self, client, db_session, persisted_user):
        """Test add position to the portfolio return 404."""
        portfolio_id = "6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b"
        ticker = "AAPL"
        quantity = 5
        price_per_share = 250
        payload = {
            "ticker": ticker,
            "quantity": quantity,
            "price_per_share": price_per_share
        }
        response = client.post(f"{PORTFOLIO_API}/{portfolio_id}/position",
                               json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.portfolio
    def test_add_position_to_portfolio_return_422(self, client, db_session, persisted_portfolio):
        """Test add position to the portfolio return 422."""
        portfolio_id = persisted_portfolio.id
        ticker = "AAPL"
        price_per_share = 250
        payload = {
            "ticker": ticker,
            "price_per_share": price_per_share
        }
        response = client.post(f"{PORTFOLIO_API}/{portfolio_id}/position",
                               json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.portfolio
    def test_read_positions_for_portfolio_return_200(self, client, portfolio_with_assets):
        """Test read position for portfolio return 200 and verify the response body."""
        portfolio_id = portfolio_with_assets["portfolio"].id
        asset_id = portfolio_with_assets["asset"].id
        position_id = portfolio_with_assets["position"].id

        asset_ticker = "NVDA"
        asset_name = "Nvidia Corp"
        asset_type = AssetType.STOCK

        expected_quantity = portfolio_with_assets["position"].quantity
        expected_price = portfolio_with_assets["position"].average_buy_price
        response = client.get(f"{PORTFOLIO_API}/{portfolio_id}/positions")

        assert_position_created(
            response=response,
            expected_position_id=position_id,
            expected_asset_id=asset_id,
            expected_portfolio_id=portfolio_id,
            expected_quantity=expected_quantity,
            expected_price=expected_price,
            expected_asset_ticker=asset_ticker,
            expected_asset_name=asset_name,
            expected_asset_type=asset_type)

    @pytest.mark.portfolio
    def test_read_positions_for_portfolio_return_404(self, client, persisted_user):
        """Test read position for portfolio return 404."""
        portfolio_id = "6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b"

        response = client.get(f"{PORTFOLIO_API}/{portfolio_id}/positions")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Portfolio not found"

    @pytest.mark.portfolio
    def test_read_transactions_for_portfolio_return_200(self, client, portfolio_with_assets):
        """ Test read transactions for portfolio return 200 and verify the response body"""
        portfolio_id = portfolio_with_assets["portfolio"].id
        transaction_id = portfolio_with_assets["transaction"].id
        asset_id = portfolio_with_assets["asset"].id

        expected_type = portfolio_with_assets["transaction"].type
        expected_quantity = portfolio_with_assets["transaction"].quantity
        expected_price_per_share = portfolio_with_assets["transaction"].price_per_share

        response = client.get(f"{PORTFOLIO_API}/{portfolio_id}/transactions")

        assert_transaction_created(
            response=response,
            expected_transaction_id=transaction_id,
            expected_asset_id=asset_id,
            expected_portfolio_id=portfolio_id,
            expected_quantity=expected_quantity,
            expected_type=expected_type,
            expected_price_per_share=expected_price_per_share)

    @pytest.mark.portfolio
    def test_read_transactions_for_portfolio_return_404(self, client):
        """Test read transactions for portfolio return 404."""
        portfolio_id = "6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b"

        response = client.get(f"{PORTFOLIO_API}/{portfolio_id}/transactions")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Transaction not found"
