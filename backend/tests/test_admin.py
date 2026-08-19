import pytest
from app.auth.models import Role, SignupStatus

def test_admin_approve_signup(client, admin_token):
    # 1. Signup
    signup_resp = client.post("/api/v1/auth/signup", json={
        "name": "To Be Approved",
        "email": "approveme@test.com",
        "password": "testpassword",
        "requested_role": "STAFF"
    })
    assert signup_resp.status_code == 201
    req_id = signup_resp.json()["id"]

    # 2. Get pending requests as Admin
    get_req_resp = client.get("/api/v1/admin/signup-requests", headers={"Authorization": f"Bearer {admin_token}"})
    assert get_req_resp.status_code == 200
    requests = get_req_resp.json()
    assert any(r["id"] == req_id for r in requests)

    # 3. Approve as MANAGER
    approve_resp = client.post(f"/api/v1/admin/signup-requests/{req_id}/approve", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "role": "MANAGER"
    })
    assert approve_resp.status_code == 200

    # 4. Login should now succeed
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "approveme@test.com",
        "password": "testpassword"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    
    # 5. Check me and verify Agent exists
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["role"] == "MANAGER"
    assert me_data["agent"] is not None

def test_admin_reject_signup(client, admin_token):
    signup_resp = client.post("/api/v1/auth/signup", json={
        "name": "To Be Rejected",
        "email": "rejectme@test.com",
        "password": "testpassword",
        "requested_role": "STAFF"
    })
    req_id = signup_resp.json()["id"]

    reject_resp = client.post(f"/api/v1/admin/signup-requests/{req_id}/reject", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "reason": "Not allowed"
    })
    assert reject_resp.status_code == 200

    login_resp = client.post("/api/v1/auth/login", data={
        "username": "rejectme@test.com",
        "password": "testpassword"
    })
    assert login_resp.status_code == 403
    assert "rejected" in login_resp.json()["detail"]

def test_admin_endpoints_forbidden_for_staff(client, admin_token):
    # Create approved staff
    signup_resp = client.post("/api/v1/auth/signup", json={
        "name": "Staff User",
        "email": "staff@test.com",
        "password": "testpassword",
        "requested_role": "STAFF"
    })
    req_id = signup_resp.json()["id"]
    client.post(f"/api/v1/admin/signup-requests/{req_id}/approve", headers={"Authorization": f"Bearer {admin_token}"}, json={"role": "STAFF"})
    
    login_resp = client.post("/api/v1/auth/login", data={"username": "staff@test.com", "password": "testpassword"})
    staff_token = login_resp.json()["access_token"]
    
    # Attempt admin endpoint
    req_resp = client.get("/api/v1/admin/signup-requests", headers={"Authorization": f"Bearer {staff_token}"})
    assert req_resp.status_code == 403
