import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database.base import Base
from app.database.session import get_db
from app.main import app

# Database URL for testing
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", 
    "postgresql+psycopg://postgres:postgres@postgres:5432/ai_governance_test"
)
# Database URL to connect to default postgres db just to create the test db
DEFAULT_DATABASE_URL = os.environ.get(
    "DEFAULT_DATABASE_URL", 
    "postgresql+psycopg://postgres:postgres@postgres:5432/postgres"
)

@pytest.fixture(scope="session")
def engine():
    # Setup: Create test database
    default_engine = create_engine(DEFAULT_DATABASE_URL, isolation_level="AUTOCOMMIT")
    try:
        with default_engine.connect() as conn:
            conn.execute(text("DROP DATABASE IF EXISTS ai_governance_test"))
            conn.execute(text("CREATE DATABASE ai_governance_test"))
    except Exception as e:
        print(f"Could not create test DB: {e}")

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Teardown
    engine.dispose()
    try:
        with default_engine.connect() as conn:
            # Need to terminate other connections to drop the DB
            conn.execute(text("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = 'ai_governance_test'
                AND pid <> pg_backend_pid();
            """))
            conn.execute(text("DROP DATABASE IF EXISTS ai_governance_test"))
    except Exception as e:
        print(f"Could not drop test DB: {e}")
    finally:
        default_engine.dispose()

@pytest.fixture(scope="function")
def db_session(engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Clean up tables after each test to ensure isolation
        with engine.connect() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                conn.execute(table.delete())
            conn.commit()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
