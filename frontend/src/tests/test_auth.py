import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_login_user():
    # First register
    client.post(
        "/auth/register",
        json={
            "username": "logintest",
            "email": "logintest@example.com",
            "password": "testpassword"
        }
    )

    # Then login
    response = client.post(
        "/auth/token",
        data={"username": "logintest", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    response = client.post(
        "/auth/token",
        data={"username": "logintest", "password": "wrongpass"},
    )
    assert response.status_code == 401
