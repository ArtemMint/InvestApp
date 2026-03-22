PORTFOLIO_API = "/api/v1/portfolio"


class TestPortfolioAPI:
    """Tests for the Portfolio CRUD endpoints."""

    def test_portfolios_returns_200(self, client, persisted_user):
        """Getting the list of portfolios should return 200 with a list body (which may be empty)."""
        response = client.get(f"{PORTFOLIO_API}/")
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert all(item["user_id"] == str(persisted_user.id) for item in body)

    def test_portfolios_returns_401_for_unauthenticated_user(self, client):
        """Getting the list of portfolios without authentication should return 401."""
        response = client.get(f"{PORTFOLIO_API}/")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_get_portfolio_by_id_returns_200(self, client, persisted_user, persisted_portfolio):
        """Getting an existing portfolio by ID should return 200 with the portfolio body."""
        response = client.get(f"{PORTFOLIO_API}/{persisted_portfolio.id}")
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == persisted_portfolio.name
        assert body["id"] == str(persisted_portfolio.id)
        assert body["user_id"] == str(persisted_user.id)
        assert body["currency"] == persisted_portfolio.currency
        assert body["is_imported"] == persisted_portfolio.is_imported

    def test_get_portfolio_by_id_returns_404(self, client, persisted_user):
        """Getting a non-existing portfolio by ID should return 404."""
        response = client.get(f"{PORTFOLIO_API}/6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b")
        assert response.status_code == 404
        assert response.json()["detail"] == "Portfolio not found"

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
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == name
        assert body["currency"] == currency
        assert body["user_id"] == str(persisted_user.id)
        assert body["is_imported"] is False

    def test_create_portfolio_returns_422(self, client, persisted_portfolio):
        """Given invalid portfolio data, should return 422."""
        payload = {
            "name": "",
            "currency": "USD",
        }
        response = client.post(f"{PORTFOLIO_API}/", json=payload)
        assert response.status_code == 422

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
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == name
        assert body["currency"] == currency
        assert body["user_id"] == str(user_id)
        assert body["id"] == str(persisted_portfolio.id)

    def test_update_portfolio_by_id_returns_404(self, client, persisted_portfolio, persisted_user):
        """Updating a non-existing portfolio should return 404."""
        name = "Updated Portfolio"
        currency = "EUR"
        user_id = str(persisted_user.id)
        payload = {
            "name": name,
            "currency": currency,
        }
        response = client.put(f"{PORTFOLIO_API}/6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b", json=payload)
        assert response.status_code == 404
        assert response.json()["detail"] == "Portfolio not found"

    def test_delete_portfolio_by_id_returns_204(self, client, persisted_portfolio):
        """Deleting an existing portfolio should return 204 with no content."""
        response = client.delete(f"{PORTFOLIO_API}/{persisted_portfolio.id}")
        assert response.status_code == 204
        assert response.content == b""

    def test_delete_portfolio_by_id_returns_404(self, client, persisted_portfolio):
        """Deleting an existing portfolio should return 204 with no content."""
        response = client.delete(f"{PORTFOLIO_API}/6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b")
        assert response.status_code == 404
        assert response.json()["detail"] == "Portfolio not found"
