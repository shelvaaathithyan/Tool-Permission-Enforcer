import pytest

def test_list_customers_empty(client):
    response = client.get("/api/v1/crm/customers")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0

def test_create_customer(client):
    customer_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com"
    }
    response = client.post("/api/v1/crm/customers", json=customer_data)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Test"
    assert "customer_id" in data
    assert "id" in data
    return data["customer_id"]

def test_create_duplicate_customer(client):
    customer_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "duplicate@example.com"
    }
    client.post("/api/v1/crm/customers", json=customer_data)
    response = client.post("/api/v1/crm/customers", json=customer_data)
    assert response.status_code == 409

def test_read_existing_customer(client):
    customer_id = test_create_customer(client)
    response = client.get(f"/api/v1/crm/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["customer_id"] == customer_id

def test_read_nonexistent_customer(client):
    response = client.get("/api/v1/crm/customers/NON-EXISTENT")
    assert response.status_code == 404

def test_update_customer(client):
    customer_id = test_create_customer(client)
    update_data = {"first_name": "UpdatedName"}
    response = client.patch(f"/api/v1/crm/customers/{customer_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["first_name"] == "UpdatedName"

def test_update_nonexistent_customer(client):
    response = client.patch("/api/v1/crm/customers/NON-EXISTENT", json={"first_name": "Test"})
    assert response.status_code == 404

def test_delete_customer(client):
    customer_id = test_create_customer(client)
    response = client.delete(f"/api/v1/crm/customers/{customer_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/v1/crm/customers/{customer_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_customer(client):
    response = client.delete("/api/v1/crm/customers/NON-EXISTENT")
    assert response.status_code == 404

def test_pagination(client):
    # Create 3 customers
    for i in range(3):
        client.post("/api/v1/crm/customers", json={
            "first_name": f"Test{i}",
            "last_name": "User",
            "email": f"test{i}@example.com"
        })
    
    response = client.get("/api/v1/crm/customers?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["page"] == 1
    
    response2 = client.get("/api/v1/crm/customers?page=2&page_size=2")
    data2 = response2.json()
    assert len(data2["items"]) == 1

def test_validation_error(client):
    # Missing required field
    response = client.post("/api/v1/crm/customers", json={"first_name": "Test"})
    assert response.status_code == 422

def test_seeded_customers(db_session, client):
    from scripts.seed import seed_customers
    
    # Run seed mechanism twice to test idempotency
    seed_customers(db_session)
    seed_customers(db_session)
    
    # List customers
    response = client.get("/api/v1/crm/customers?page_size=20")
    assert response.status_code == 200
    data = response.json()
    
    # Verify 13 customers exist
    assert data["total"] >= 13
    customer_ids = [c["customer_id"] for c in data["items"]]
    for i in range(1, 15):
        # Note: Sumathi (CUST-004) was removed from DEMO_CUSTOMERS in seed.py 
        # so CUST-004 won't exist. Wait, if she was removed, then the IDs are 1 to 14, skipping 4!
        if i == 4:
            continue
        assert f"CUST-{i:03d}" in customer_ids
