import pytest
from app.auth.models import Role

def test_signup_manager(client):
    response = client.post("/api/v1/auth/signup", json={
        "name": "Test Manager",
        "email": "manager@test.com",
        "password": "testpassword",
        "role": "MANAGER"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "manager@test.com"
    assert data["role"] == "MANAGER"
    assert "password" not in data
    assert "password_hash" not in data
    assert "agent" in data
    assert data["agent"] is not None

def test_signup_duplicate_email(client):
    client.post("/api/v1/auth/signup", json={
        "name": "Test Manager",
        "email": "duplicate@test.com",
        "password": "testpassword",
        "role": "MANAGER"
    })
    response = client.post("/api/v1/auth/signup", json={
        "name": "Another",
        "email": "duplicate@test.com",
        "password": "testpassword",
        "role": "STAFF"
    })
    assert response.status_code == 409

def test_signup_admin_forbidden(client):
    response = client.post("/api/v1/auth/signup", json={
        "name": "Test Admin",
        "email": "admin@test.com",
        "password": "testpassword",
        "role": "ADMIN"
    })
    assert response.status_code == 403

def test_login_success(client):
    client.post("/api/v1/auth/signup", json={
        "name": "Login User",
        "email": "login@test.com",
        "password": "testpassword",
        "role": "STAFF"
    })
    response = client.post("/api/v1/auth/login", data={
        "username": "login@test.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_invalid(client):
    response = client.post("/api/v1/auth/login", data={
        "username": "nonexistent@test.com",
        "password": "wrong"
    })
    assert response.status_code == 401

def test_get_me(client):
    client.post("/api/v1/auth/signup", json={
        "name": "Me User",
        "email": "me@test.com",
        "password": "testpassword",
        "role": "STAFF"
    })
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "me@test.com",
        "password": "testpassword"
    })
    token = login_resp.json()["access_token"]
    
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["email"] == "me@test.com"

def test_get_me_unauthenticated(client):
    me_resp = client.get("/api/v1/auth/me")
    assert me_resp.status_code == 401
