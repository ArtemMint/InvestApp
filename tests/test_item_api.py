from datetime import datetime

ITEM_API = "/api/v1/items"


class TestItemAPI:
    """Tests for the Item CRUD endpoints."""

    def test_list_items_returns_200(self, client):
        """Getting the list of items should return 200 with a list body (which may be empty)."""
        response = client.get(f"{ITEM_API}/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_item_by_id_returns_200(self, client, persisted_item):
        """Getting an existing item by ID should return 200 with the item body."""
        response = client.get(f"{ITEM_API}/{persisted_item.id}")
        assert response.status_code == 200
        body = response.json()
        assert body["title"] == persisted_item.title
        assert body["description"] == persisted_item.description
        assert body["media_url"] == persisted_item.media_url

    def test_get_item_by_id_returns_404(self, client, persisted_item):
        """Getting non-existing item by ID should return 404."""
        response = client.get(f"{ITEM_API}/999")
        assert response.status_code == 404

    def test_create_item_returns_201(self, client):
        """Given valid item data, should return 201 with the created item body, which includes id and timestamps."""
        title = "My Item"
        description = "Super unique item"
        media_url = "My URL"
        payload = {
            "title": title,
            "description": description,
            "media_url": media_url
        }
        response = client.post(f"{ITEM_API}/",
                               json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["title"] == title
        assert body["description"] == description
        assert body["media_url"] == media_url

    def test_create_item_returns_422(self, client):
        """Given invalid item data, should return 422."""
        payload = {
            "title": "",
            "media_url": "My URL"
        }
        response = client.post(f"{ITEM_API}/", json=payload)
        assert response.status_code == 422

    def test_update_item_by_id_returns_200(self, client, persisted_item):
        """Updating an existing item should return 200 with the updated item body."""
        title = "Update title"
        description = "Updated descr"
        media_url = "Updated URL"
        id = persisted_item.id
        payload = {
            "title": title,
            "description": description,
            "media_url": media_url,
            "id": id
        }
        response = client.put(f"{ITEM_API}", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == id
        assert body["title"] == title
        assert body["description"] == description
        assert body["media_url"] == media_url

    def test_update_item_by_id_returns_400(self, client, persisted_item):
        """Updating an existing item should return 400 with the updated item body."""
        payload = {
            "id": None,
            "title": "Updated Title",
            "description": "Updated description"
        }
        response = client.put(f"{ITEM_API}/", json=payload)
        assert response.status_code == 400
        assert response.json()["detail"] == "id is required for update"

    def test_update_item_by_id_returns_404(self, client, persisted_item):
        """Updating an existing item should return 200 with the updated item body."""
        payload = {
            "id": 4,
            "title": "Updated Title",
            "description": "Updated description"
        }
        response = client.put(f"{ITEM_API}/", json=payload)
        assert response.status_code == 404
        assert response.json()["detail"] == "Item not found"

    def test_delete_item_by_id_returns_204(self, client, persisted_item):
        """Deleting an existing item should return 204 with no content."""
        response = client.delete(f"{ITEM_API}/{persisted_item.id}")
        assert response.status_code == 204
        assert response.content == b'null'

    def test_delete_item_by_id_returns_404(self, client, persisted_item):
        """Deleting an existing item should return 204 with no content."""
        response = client.delete(f"{ITEM_API}/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Item not found"
