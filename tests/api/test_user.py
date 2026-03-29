import pytest
from fastapi import status

USER_API = "/api/v1/users"


class TestUserAPI:

    @pytest.mark.users
    def test_get_users_returns_200(self, client, persisted_user):
        """Getting an existing user by email should return 200 with the user body."""
        response = client.get(f"{USER_API}/{persisted_user.email}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == persisted_user.email

    @pytest.mark.users
    def test_get_users_returns_404(self, client, persisted_user):
        """Getting non-existing user by email should return 404."""
        response = client.get(f"{USER_API}/{'test_test@gmail.com'}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.users
    def test_register_user_returns_201(self, client):
        """Registering a new user with unique email should return 201 with the created user body."""
        email = "new_user@gmail.com"
        password = "new_password"
        response = client.post(f"{USER_API}/register",
                               json={"email": email,
                                     "password": password})
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.users
    def test_register_user_returns_400(self, client, persisted_user):
        """Registering a user with an email that already exists should return 400."""
        response = client.post(f"{USER_API}/register",
                               json={"email": persisted_user.email,
                                     "password": "any_password"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.users
    def test_change_password_returns_200(self, client, persisted_user):
        """Changing password for an existing user should return 200 with the updated user body."""
        new_password = "new_test_password"
        response = client.put(f"{USER_API}/password",
                              json={"email": persisted_user.email,
                                    "password": new_password})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == persisted_user.email

    @pytest.mark.users
    def test_change_password_returns_404(self, client, persisted_user):
        """Changing password for a non-existing user should return 404."""
        email = "new_user@gmail.com"
        new_password = "new_test_password"
        response = client.put(f"{USER_API}/password",
                              json={"email": email,
                                    "password": new_password})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.users
    def test_user_login_returns_200(self, client):
        """Logging in with correct credentials should return 200."""
        email = "new_user@gmail.com"
        password = "new_password"
        response = client.post(f"{USER_API}/register",
                               json={"email": email,
                                     "password": password})
        assert response.status_code == status.HTTP_201_CREATED
        response = client.post(f"{USER_API}/login",
                               data={"username": email,
                                     "password": password})
        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get("access_token") is not None
        assert response.cookies.get("access_token").startswith("\"Bearer")
        assert response.json()["user"]['email'] == email

    @pytest.mark.users
    def test_user_login_returns_401(self, client):
        """Logging in with incorrect credentials should return 401."""
        email = "new@gmail.com"
        password = "new_password"
        response = client.post(f"{USER_API}/login",
                               data={"username": email,
                                     "password": password})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.users
    def test_user_logout_returns_200(self, client, persisted_user):
        """Logging out with an authorization token should return 200 and confirm message."""
        response = client.post(f"{USER_API}/logout")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["msg"] == "test_user@gmail.com logged out"

    @pytest.mark.users
    def test_user_logout_returns_401(self, client):
        """Logging out without an authorization token should return 401."""
        response = client.post(f"{USER_API}/logout")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.users
    def test_delete_user_by_id(self, client, persisted_user):
        """Deleting an existing user by ID should return 204 with no content."""
        response = client.delete(f"{USER_API}/{persisted_user.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    # def test_get_current_user_returns_200(self, client, persisted_user):
    #     """Getting current user with valid token should return 200 with user body."""
    #     response = client.get(f"{USER_API}/me")
    #     assert response.status_code == status.HTTP_200_OK
    #     assert response.json()["email"] == persisted_user.email
    #     assert response.json()["id"] == str(persisted_user.id)

    # def test_get_current_user_returns_401(self, client):
    #     """Getting current user without token should return 401."""
    #     client.cookies.clear()  # Clear any existing cookies to simulate no token
    #     response = client.get(f"{USER_API}/me")
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED
