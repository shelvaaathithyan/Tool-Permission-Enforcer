import sys
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.crm.models import Customer
from app.auth.models import User, Role
from app.agent.models import Agent
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROD_DATABASE_URL = "postgresql+psycopg://postgres:Shelvaaathithyan1234@database-1.cti8agos83e5.ap-south-1.rds.amazonaws.com:5432/postgres?sslmode=require"

CUSTOMERS = [
    ("CUST-100", "Arun", "Kumar", "Apex Technologies", "Software Engineer", "arun.kumar@example.com", "ACTIVE"),
    ("CUST-101", "Priya", "Sharma", "Bright Solutions", "Product Manager", "priya.sharma@example.com", "ACTIVE"),
    ("CUST-102", "Rahul", "Verma", "Vertex Labs", "Engineering Manager", "rahul.verma@example.com", "ACTIVE"),
    ("CUST-103", "Ananya", "Rao", "Nova Systems", "UX Designer", "ananya.rao@example.com", "ACTIVE"),
    ("CUST-104", "Vikram", "Singh", "Orion Technologies", "DevOps Engineer", "vikram.singh@example.com", "INACTIVE"),
    ("CUST-105", "Meera", "Krishnan", "DataWorks Inc.", "Data Scientist", "meera.krishnan@example.com", "ACTIVE"),
    ("CUST-106", "Suresh", "Kumar", "CloudBridge", "Cloud Architect", "suresh.kumar@example.com", "ACTIVE"),
    ("CUST-107", "Kavya", "Nair", "GreenTech Solutions", "Marketing Manager", "kavya.nair@example.com", "ACTIVE"),
    ("CUST-108", "Arjun", "Patel", "FinEdge Systems", "Financial Analyst", "arjun.patel@example.com", "ACTIVE"),
    ("CUST-109", "Divya", "Menon", "Global Solutions", "HR Manager", "divya.menon@example.com", "INACTIVE"),
    ("CUST-110", "Karthik", "Raj", "Alpha Networks", "Network Engineer", "karthik.raj@example.com", "ACTIVE"),
    ("CUST-111", "Sneha", "Iyer", "DigitalWorks", "Business Analyst", "sneha.iyer@example.com", "ACTIVE"),
    ("CUST-112", "Naveen", "Kumar", "CoreStack Technologies", "Security Engineer", "naveen.kumar@example.com", "ACTIVE"),
    ("CUST-113", "Harini", "S", "InnovateWorks", "Project Manager", "harini.s@example.com", "ACTIVE"),
    ("CUST-114", "Dinesh", "R", "TechBridge", "QA Lead", "dinesh.r@example.com", "ACTIVE"),
    ("CUST-115", "Keerthana", "P", "BluePeak Systems", "Solutions Architect", "keerthana.p@example.com", "ACTIVE"),
    ("CUST-116", "Manoj", "V", "Zeta Ventures", "Technical Lead", "manoj.v@example.com", "ACTIVE"),
    ("CUST-117", "Swathi", "R", "CloudNova", "Product Designer", "swathi.r@example.com", "INACTIVE"),
    ("CUST-118", "Sanjay", "Kumar", "Pioneer Apps", "Backend Developer", "sanjay.kumar@example.com", "ACTIVE"),
    ("CUST-119", "Lakshmi", "P", "Epsilon Group", "Operations Manager", "lakshmi.p@example.com", "ACTIVE"),
]

AGENTS = [
    ("agent-ravi-001", "Ravi S CRM Assistant", "Ravi S", Role.STAFF, "ACTIVE", "ravi.s@example.com"),
    ("agent-neha-002", "Neha P CRM Assistant", "Neha P", Role.STAFF, "ACTIVE", "neha.p@example.com"),
    ("agent-mohan-003", "Mohan R CRM Assistant", "Mohan R", Role.STAFF, "ACTIVE", "mohan.r@example.com"),
    ("agent-divya-004", "Divya K CRM Assistant", "Divya K", Role.STAFF, "ACTIVE", "divya.k@example.com"),
    ("agent-ajay-005", "Ajay M CRM Assistant", "Ajay M", Role.STAFF, "ACTIVE", "ajay.m@example.com"),
    ("agent-pooja-006", "Pooja V CRM Assistant", "Pooja V", Role.STAFF, "ACTIVE", "pooja.v@example.com"),
    ("agent-suresh-007", "Suresh B CRM Assistant", "Suresh B", Role.MANAGER, "ACTIVE", "suresh.b@example.com"),
    ("agent-ramesh-008", "Ramesh T CRM Assistant", "Ramesh T", Role.MANAGER, "ACTIVE", "ramesh.t@example.com"),
    ("agent-kiran-009", "Kiran J CRM Assistant", "Kiran J", Role.STAFF, "ACTIVE", "kiran.j@example.com"),
    ("agent-admin-010", "System Administrator", "System Administrator", Role.ADMIN, "ACTIVE", "admin@example.com"),
]

def seed_data():
    engine = create_engine(PROD_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    customers_before = db.query(Customer).count()
    users_before = db.query(User).count()
    agents_before = db.query(Agent).count()
    
    customers_created = 0
    customers_skipped = 0
    users_created = 0
    users_skipped = 0
    agents_created = 0
    agents_skipped = 0

    try:
        logger.info("Starting safe demo data seeder...")

        # 1. Customers
        for cid, fname, lname, comp, desig, email, status in CUSTOMERS:
            # Query by email to ensure no duplicates
            existing = db.query(Customer).filter(Customer.email == email).first()
            if existing:
                customers_skipped += 1
                continue
            
            c = Customer(
                customer_id=cid,
                first_name=fname,
                last_name=lname,
                company=comp,
                designation=desig,
                email=email,
                session_status=status
            )
            db.add(c)
            customers_created += 1

        # 2. Staff/Agents
        pwd = get_password_hash("demo123")
        
        for aid, aname, uname, urole, status, email in AGENTS:
            # Query User by email
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                users_skipped += 1
                user_record = existing_user
            else:
                user_record = User(
                    name=uname,
                    email=email,
                    password_hash=pwd,
                    role=urole,
                    is_active=(status == "ACTIVE")
                )
                db.add(user_record)
                db.flush()
                users_created += 1

            # Query Agent by agent_id or user_id
            existing_agent = db.query(Agent).filter((Agent.agent_id == aid) | (Agent.user_id == user_record.id)).first()
            if existing_agent:
                agents_skipped += 1
            else:
                agent_record = Agent(
                    agent_id=aid,
                    user_id=user_record.id,
                    name=aname,
                    is_active=(status == "ACTIVE")
                )
                db.add(agent_record)
                agents_created += 1

        db.commit()
        logger.info("Demo data seeding completed successfully.")

    except Exception as e:
        db.rollback()
        logger.error(f"Error during seeding, transaction rolled back: {e}")
        raise e
    finally:
        customers_after = db.query(Customer).count()
        users_after = db.query(User).count()
        agents_after = db.query(Agent).count()
        
        print("\n==================================================")
        print("SEEDING REPORT")
        print("==================================================")
        print(f"Customers: {customers_before} before -> {customers_after} after")
        print(f"  Created: {customers_created}")
        print(f"  Skipped: {customers_skipped}")
        print()
        print(f"Users: {users_before} before -> {users_after} after")
        print(f"  Created: {users_created}")
        print(f"  Skipped: {users_skipped}")
        print()
        print(f"Agents: {agents_before} before -> {agents_after} after")
        print(f"  Created: {agents_created}")
        print(f"  Skipped: {agents_skipped}")
        print("==================================================")
        db.close()

if __name__ == "__main__":
    seed_data()
