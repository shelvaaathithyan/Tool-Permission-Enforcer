import os
import sys

# Add backend directory to sys.path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.crm.models import Customer
from app.auth.models import User, Role
from app.agent.models import Agent

# Production DB URL identified earlier
PROD_DATABASE_URL = "postgresql+psycopg://postgres:Shelvaaathithyan1234@database-1.cti8agos83e5.ap-south-1.rds.amazonaws.com:5432/postgres?sslmode=require"

engine = create_engine(PROD_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def inspect_db():
    print("==================================================")
    print("CURRENT DATABASE COUNTS (postgres)")
    print("==================================================")
    db = SessionLocal()
    try:
        customers_count = db.query(Customer).count()
        users_count = db.query(User).count()
        agents_count = db.query(Agent).count()
        
        print(f"Customers: {customers_count}")
        print(f"Users: {users_count}")
        print(f"Agents: {agents_count}")
        print()

        print("==================================================")
        print("EXISTING CUSTOMERS")
        print("==================================================")
        customers = db.query(Customer).all()
        for c in customers:
            print(f"- {c.first_name} {c.last_name} | {c.email} | ID: {c.customer_id}")
        print()

        print("==================================================")
        print("EXISTING USERS/ROLES")
        print("==================================================")
        users = db.query(User).all()
        for u in users:
            print(f"- {u.name} | {u.email} | Role: {u.role.name if u.role else 'None'} | Active: {u.is_active}")
        print()

        print("==================================================")
        print("EXISTING AGENTS")
        print("==================================================")
        agents = db.query(Agent).all()
        for a in agents:
            print(f"- {a.name} | ID: {a.agent_id} | UserID: {a.user_id} | Active: {a.is_active}")
        print()
        
    finally:
        db.close()

if __name__ == "__main__":
    inspect_db()
