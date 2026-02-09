import pytest
import requests

from app.utils.helpers import log_request, timing

BASE_URL = "http://127.0.0.1:8000"
ITEM_API = "/api/v1/items"

class TestItemAPI:
    """
    Test the main endpoint for the Item API.
    """

    @pytest.fixture(scope="class")
    def session(self):
        """Fixture to provide a requests session for all tests in the class."""
        s = requests.Session()
        # Potential authentication or header setup can go here
        yield s
        # Teardown logic if needed (e.g., closing the session)
        s.close()

    def test_status_code(self, session):
        """Test that the main endpoint returns a 200 OK status code."""
        response = session.get(f"{BASE_URL}/health")
        assert response.status_code == 200

    def test_item_create(self, session):
        """Test that the main endpoint returns a 200 OK status code."""
        response = session.post(f"{BASE_URL}{ITEM_API}",
                                json={"title": "Test Item",
                                      "description": "Test Item description"})
        assert response.status_code == 200

    def test_data_structure(self, session):
        """Test the structure of the data returned from an endpoint."""
        response = session.get(f"{BASE_URL}{ITEM_API}")
        assert response.status_code == 200
        data = response.json()[0]
        assert "id" in data
        assert "title" in data
        assert "description" in data

    def test_get_item(self, session):
        """Test that the main endpoint returns a 200 OK status code."""
        response = session.get(f"{BASE_URL}{ITEM_API}/1")
        assert response.status_code == 200
        data = response.json()[0]
        assert "id" in data
        assert "title" in data
        assert "description" in data

    def test_item_update(self, session):
        """Test that the main endpoint returns a 200 OK status code."""
        response = session.put(f"{BASE_URL}{ITEM_API}",
                               json={"title": "Test Item",
                                     "id": 0})
        assert response.status_code == 200
        assert response.json()["title"] == "Test Item"
