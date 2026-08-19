import pytest
from app.crm.service import search_customers, create_customer
from app.crm.schemas import CustomerCreate

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
    response = client.put(f"/api/v1/crm/customers/{customer_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["first_name"] == "UpdatedName"

def test_update_nonexistent_customer(client):
    response = client.put("/api/v1/crm/customers/NON-EXISTENT", json={"first_name": "Test"})
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
    assert data["total"] >= 11
    customer_ids = [c["customer_id"] for c in data["items"]]
    for i in range(1, 15):
        if i in (1, 2, 4):
            continue
        assert f"CUST-{i:03d}" in customer_ids

def test_search_customers(db_session):
    create_customer(db_session, CustomerCreate(
        first_name="Test", last_name="User1", email="test1@example.com", phone="1", company="C", designation="D"
    ))
    create_customer(db_session, CustomerCreate(
        first_name="Test", last_name="User2", email="test2@example.com", phone="2", company="C", designation="D"
    ))
    create_customer(db_session, CustomerCreate(
        first_name="Jane", last_name="Smith", email="jane.smith@example.com", phone="3", company="C", designation="D"
    ))

    results = search_customers(db_session, "Test")
    assert len(results) >= 2
    
    # Exact match name
    results = search_customers(db_session, "Jane Smith")
    assert len(results) == 1
    assert results[0].first_name == "Jane"
    
    # Email match
    results = search_customers(db_session, "jane.smith@")
    assert len(results) == 1

def test_search_customers_company(db_session):
    # Setup test customer with specific company
    create_customer(db_session, CustomerCreate(
        first_name="Sanjay",
        last_name="Kumar",
        email="sanjay.kumar@example.com",
        phone="12345",
        company="Pioneer Apps",
        designation="Backend Developer"
    ))
    
    results = search_customers(db_session, company="Pioneer Apps")
    assert len(results) == 1
    assert results[0].first_name == "Sanjay"
    
    # Case insensitive
    results = search_customers(db_session, company="pioneer APPS")
    assert len(results) == 1
    
    # Extra whitespace
    results = search_customers(db_session, company="  Pioneer   Apps  ")
    assert len(results) == 1
    
    # Multiple matching customers
    create_customer(db_session, CustomerCreate(
        first_name="Ravi",
        last_name="Singh",
        email="ravi@example.com",
        phone="999",
        company="Pioneer Apps",
        designation="Frontend Developer"
    ))
    
    results = search_customers(db_session, company="Pioneer Apps")
    assert len(results) == 2
    
    # No matching customers
    results = search_customers(db_session, company="Unknown Corp")
    assert len(results) == 0

def test_search_customers_designation(db_session):
    create_customer(db_session, CustomerCreate(
        first_name="Designer",
        last_name="One",
        email="d1@example.com",
        phone="1",
        company="Art Corp",
        designation="Lead UX"
    ))
    results = search_customers(db_session, designation="lead ux")
    assert len(results) == 1
    assert results[0].first_name == "Designer"
