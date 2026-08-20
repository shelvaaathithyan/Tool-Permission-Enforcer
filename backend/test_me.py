import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["GEMINI_API_KEY"] = "fake-key"
os.environ["SECRET_KEY"] = "fake_secret_key"
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database.base import Base
from app.database.session import get_db
from app.auth.service import create_user_and_agent
from app.auth.models import Role
from app.core.security import get_password_hash

# Setup test DB
engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def run_test():
    db = TestingSessionLocal()
    try:
        # Create a user
        user = create_user_and_agent(db, "Test User", "test@example.com", get_password_hash("password"), Role.STAFF)
        
        # Login to get token
        login_res = client.post("/api/v1/auth/login", data={"username": "test@example.com", "password": "password"})
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        
        # Test GET /me
        me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        assert me_res.json()["name"] == "Test User"
        
        # Test PATCH /me
        patch_res = client.patch("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}, json={"name": "New Name"})
        assert patch_res.status_code == 200, f"PATCH failed: {patch_res.text}"
        assert patch_res.json()["name"] == "New Name"
        
        # Verify changes persisted
        me_res2 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res2.json()["name"] == "New Name"
        
        # Verify you can't update other fields
        patch_res2 = client.patch("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}, json={"name": "New Name 2", "email": "hacked@example.com", "role": "ADMIN"})
        assert patch_res2.status_code == 200
        data2 = patch_res2.json()
        assert data2["name"] == "New Name 2"
        assert data2["email"] == "test@example.com" # Should not be hacked
        assert data2["role"] == "STAFF" # Should not be ADMIN
        
        print("SUCCESS! Test passed perfectly.")
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        try:
            os.remove("test.db")
        except:
            pass

if __name__ == "__main__":
    run_test()
