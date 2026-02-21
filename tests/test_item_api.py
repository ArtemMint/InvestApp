import pytest

ITEM_API = "/api/v1/items"


class TestItemAPI:
    """
    Test the main endpoint for the Item API.
    """

    def test_status_code(self, client):
        """Test that the health endpoint returns a 200 OK status code."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_item_create(self, client):
        """Test that creating an item returns a 201 Created status code."""
        response = client.post(
            ITEM_API,
            json={"title": "Test Item", "description": "Test Item description"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Item"
        assert data["description"] == "Test Item description"

    def test_data_structure(self, client):
        """Test the structure of the data returned from an endpoint."""
        # First create an item
        client.post(
            ITEM_API,
            json={"title": "Test Item for Structure", "description": "Description"}
        )

        # Then get all items
        response = client.get(ITEM_API)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            item = data[0]
            assert "id" in item
            assert "title" in item
            assert "description" in item

    def test_get_item(self, client):
        """Test that getting a specific item works correctly."""
        # First create an item
        create_response = client.post(
            ITEM_API,
            json={"title": "Test Get Item", "description": "Description for get"}
        )
        created_item = create_response.json()
        item_id = created_item["id"]

        # Then get the specific item
        response = client.get(f"{ITEM_API}/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "title" in data
        assert data["id"] == item_id

    def test_item_update(self, client):
        """Test that updating an item works correctly."""
        # First create an item
        create_response = client.post(
            ITEM_API,
            json={"title": "Original Title", "description": "Original Description"}
        )
        created_item = create_response.json()
        item_id = created_item["id"]

        # Then update it
        response = client.put(
            ITEM_API,
            json={"title": "Updated Title", "id": item_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
