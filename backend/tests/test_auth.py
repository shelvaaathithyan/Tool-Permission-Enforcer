import pytest
from app.auth.models import Role

def test_signup_manager(client):
    response = client.post("/api/v1/auth/signup", json={
        "name": "Test Manager",
        "email": "manager@test.com",
        "password": "testpassword",
        "requested_role": "MANAGER"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "manager@test.com"
    assert data["requested_role"] == "MANAGER"
    assert data["status"] == "PENDING"
    assert "password" not in data
    assert "password_hash" not in data
    assert "agent" not in data

def test_signup_duplicate_email(client):
    client.post("/api/v1/auth/signup", json={
        "name": "Test Manager",
        "email": "duplicate@test.com",
        "password": "testpassword",
        "requested_role": "MANAGER"
    })
    response = client.post("/api/v1/auth/signup", json={
        "name": "Another",
        "email": "duplicate@test.com",
        "password": "testpassword",
        "requested_role": "STAFF"
    })
    assert response.status_code == 409

def test_signup_admin_forbidden(client):
    response = client.post("/api/v1/auth/signup", json={
        "name": "Test Admin",
        "email": "admin@test.com",
        "password": "testpassword",
        "requested_role": "ADMIN"
    })
    assert response.status_code == 403

def test_login_pending_fails(client):
    client.post("/api/v1/auth/signup", json={
        "name": "Pending User",
        "email": "pending@test.com",
        "password": "testpassword",
        "requested_role": "STAFF"
    })
    response = client.post("/api/v1/auth/login", data={
        "username": "pending@test.com",
        "password": "testpassword"
    })
    assert response.status_code == 403
    assert "awaiting administrator approval" in response.json()["detail"]

def test_login_invalid(client):
    response = client.post("/api/v1/auth/login", data={
        "username": "nonexistent@test.com",
        "password": "wrong"
    })
    assert response.status_code == 401

def test_get_me(client, admin_token):
    # Create approved user
    signup_resp = client.post("/api/v1/auth/signup", json={
        "name": "Me User",
        "email": "me@test.com",
        "password": "testpassword",
        "requested_role": "STAFF"
    })
    req_id = signup_resp.json()["id"]
    client.post(f"/api/v1/admin/signup-requests/{req_id}/approve", headers={"Authorization": f"Bearer {admin_token}"}, json={"role": "STAFF"})

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
