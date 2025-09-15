import pytest
from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "tenant_name": "New Organization"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "tenant_id" in data


def test_register_duplicate_email(client: TestClient, test_user):
    """Test registration with duplicate email"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "password": "somepassword123",
            "tenant_name": "Another Organization"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["error"]["message"]


def test_login_valid_credentials(client: TestClient, test_user):
    """Test login with valid credentials"""
    response = client.post(
        "/api/v1/auth/login/json",
        json={
            "email": test_user.email,
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


def test_login_invalid_credentials(client: TestClient, test_user):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login/json",
        json={
            "email": test_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["error"]["message"]


def test_login_nonexistent_user(client: TestClient):
    """Test login with nonexistent user"""
    response = client.post(
        "/api/v1/auth/login/json",
        json={
            "email": "nonexistent@example.com",
            "password": "somepassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["error"]["message"]


def test_get_current_user(client: TestClient, auth_headers):
    """Test getting current user"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert "tenant_id" in data


def test_get_current_user_unauthorized(client: TestClient):
    """Test getting current user without authentication"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_change_password(client: TestClient, auth_headers):
    """Test changing password"""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "testpassword123",
            "new_password": "newtestpassword123"
        }
    )
    assert response.status_code == 200
    assert "successfully" in response.json()["message"]


def test_change_password_wrong_current(client: TestClient, auth_headers):
    """Test changing password with wrong current password"""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "wrongpassword",
            "new_password": "newtestpassword123"
        }
    )
    assert response.status_code == 400
    assert "Incorrect current password" in response.json()["error"]["message"]


def test_create_api_token(client: TestClient, auth_headers):
    """Test creating API token"""
    response = client.post(
        "/api/v1/auth/api-tokens",
        headers=auth_headers,
        json={
            "name": "Test API Token",
            "scopes": ["read", "write"],
            "expires_in_days": 30
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test API Token"
    assert "token" in data
    assert data["scopes"] == ["read", "write"]


def test_list_api_tokens(client: TestClient, auth_headers):
    """Test listing API tokens"""
    # First create a token
    client.post(
        "/api/v1/auth/api-tokens",
        headers=auth_headers,
        json={"name": "Test Token"}
    )
    
    # Then list tokens
    response = client.get("/api/v1/auth/api-tokens", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "Test Token"


def test_refresh_token(client: TestClient, test_user):
    """Test refreshing access token"""
    # First login to get tokens
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={
            "email": test_user.email,
            "password": "testpassword123"
        }
    )
    assert login_response.status_code == 200
    refresh_token = login_response.json()["refresh_token"]
    
    # Use refresh token to get new access token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_invalid_token(client: TestClient):
    """Test refreshing with invalid token"""
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"}
    )
    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["error"]["message"]