import pytest
from fastapi import status

from app.models.asset import AssetType
from tests.utils.assertions import assert_asset_created

ASSETS_API = "/api/v1/assets"


class TestAssetAPI:
    """Tests for the Asset CRUD endpoints."""

    @pytest.mark.assets
    def test_read_assets_returns_200(self, client, persisted_asset):
        """

        :param client:
        :param persisted_asset:
        :return:
        """
        response = client.get(f"{ASSETS_API}/")
        body = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(body, list)
        assert all(item["id"] == str(persisted_asset.id) for item in body)

    @pytest.mark.assets
    def test_read_assets_returns_404(self, client):
        """

        :param client:
        :return:
        """
        response = client.get(f"{ASSETS_API}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.assets
    def test_read_asset_returns_200(self, client, persisted_asset):
        """

        :param client:
        :param persisted_asset:
        :return:
        """
        expected_asset_id = persisted_asset.id
        expected_asset_name = persisted_asset.name
        expected_asset_ticker = persisted_asset.ticker
        expected_asset_type = persisted_asset.asset_type
        response = client.get(f"{ASSETS_API}/{expected_asset_ticker}")
        assert_asset_created(
            response=response,
            expected_asset_id=expected_asset_id,
            expected_asset_name=expected_asset_name,
            expected_asset_type=expected_asset_type,
            expected_asset_ticker=expected_asset_ticker)

    @pytest.mark.assets
    def test_read_asset_returns_404(self, client):
        """

        :param client:
        :return:
        """
        response = client.get(f"{ASSETS_API}/6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.assets
    def test_add_asset_return_201(self, client):
        """

        :param client:
        :return:
        """
        ticker = "GOOGL"
        name = "GOOGL"
        asset_type = AssetType.STOCK
        payload = {
            "ticker": ticker,
            "name": name,
            "asset_type": asset_type
        }
        response = client.post(f"{ASSETS_API}", json=payload)
        body = response.json()
        assert response.status_code == status.HTTP_201_CREATED, response.status_code
        assert body["name"] == name
        assert body["ticker"] == ticker
        assert body["asset_type"] == asset_type

    @pytest.mark.assets
    def test_add_asset_return_400(self, client, persisted_asset):
        """

        :param client:
        :return:
        """
        ticker = "GOOG"
        name = "Google"
        asset_type = AssetType.STOCK
        payload = {
            "ticker": ticker,
            "name": name,
            "asset_type": asset_type
        }
        response = client.post(f"{ASSETS_API}", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['detail'] == "Asset already created"

    @pytest.mark.assets
    def test_update_asset_by_id_return_200(self, client, persisted_asset):
        """

        :param client:
        :return:
        """
        ticker = "NFLX"
        name = "Netflix"
        asset_type = AssetType.STOCK
        payload = {
            "ticker": ticker,
            "name": name,
            "asset_type": asset_type
        }
        response = client.put(f"{ASSETS_API}/id/{persisted_asset.id}", json=payload)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.assets
    def test_update_asset_by_id_return_404(self, client, persisted_asset):
        """

        :param client:
        :return:
        """
        ticker = "NFLX"
        name = "Netflix"
        asset_type = AssetType.STOCK
        payload = {
            "ticker": ticker,
            "name": name,
            "asset_type": asset_type
        }
        response = client.put(f"{ASSETS_API}/id/6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b", json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.assets
    def test_update_asset_by_ticker_return_200(self, client, persisted_asset):
        """

        :param client:
        :return:
        """
        ticker = "NFLX"
        name = "Netflix"
        asset_type = AssetType.STOCK
        payload = {
            "ticker": ticker,
            "name": name,
            "asset_type": asset_type
        }
        response = client.put(f"{ASSETS_API}/ticker/{persisted_asset.ticker}", json=payload)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.assets
    def test_update_asset_by_ticker_return_404(self, client, persisted_asset):
        """

        :param client:
        :return:
        """
        ticker = "NFLX"
        name = "Netflix"
        asset_type = AssetType.STOCK
        payload = {
            "ticker": ticker,
            "name": name,
            "asset_type": asset_type
        }
        response = client.put(f"{ASSETS_API}/ticker/6ec0bd7f-11c0-43da-975e-2a8ad9ebae0b", json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.assets
    def test_add_asset_return_422(self, client):
        """

        :param client:
        :return:
        """
        ticker = "GOOGL"
        asset_type = AssetType.STOCK
        payload = {
            "ticker": ticker,
            "asset_type": asset_type
        }
        response = client.post(f"{ASSETS_API}", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.assets
    def test_remove_asset_by_id_return_204(self, client, persisted_asset):
        """

        :param client:
        :return:
        """
        response = client.delete(f"{ASSETS_API}/id/{persisted_asset.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.assets
    def test_remove_asset_by_ticker_return_204(self, client, persisted_asset):
        """

        :param client:
        :return:
        """
        response = client.delete(f"{ASSETS_API}/ticker/{persisted_asset.ticker}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
