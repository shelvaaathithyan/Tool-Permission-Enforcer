import sys
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.crm.models import Customer
from app.crm.schemas import CustomerCreate
from app.crm import service
from app.database.session import SessionLocal
from app.auth.models import User, Role
from app.agent.models import Agent
from app.core.security import get_password_hash
import uuid


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEMO_CUSTOMERS = [
    {
        "customer_id": "CUST-001",
        "first_name": "Shelvaaathithyan",
        "last_name": "VK",
        "email": "shelvaaathithyan.vk@example.com",
        "phone": "+91-9000000001",
        "company": "ABC Technologies",
        "designation": "Software Engineer",
        "date_of_birth": "1995-05-15",
    },
    {
        "customer_id": "CUST-002",
        "first_name": "Swathi",
        "last_name": "Laxmi",
        "email": "swathi.laxmi@example.com",
        "phone": "+91-9000000002",
        "company": "XYZ Solutions",
        "designation": "Engineering Manager",
        "date_of_birth": "1994-08-20",
    },
    {
        "customer_id": "CUST-003",
        "first_name": "Karthikeyan",
        "last_name": "VV",
        "email": "karthikeyan.vv@example.com",
        "phone": "+91-9000000003",
        "company": "Acme Corporation",
        "designation": "Product Manager",
        "date_of_birth": "1993-11-10",
    },
    {
        "customer_id": "CUST-004",
        "first_name": "Sumathi",
        "last_name": "P",
        "email": "sumathi.p@example.com",
        "phone": "+91-9000000004",
        "company": "Tech Innovators",
        "designation": "Senior Developer",
        "date_of_birth": "1990-02-25",
    },
    {
        "customer_id": "CUST-005",
        "first_name": "Mohana Kumar",
        "last_name": "P",
        "email": "mohana.kumar@example.com",
        "phone": "+91-9000000005",
        "company": "Global Solutions",
        "designation": "Systems Architect",
        "date_of_birth": "1988-06-12",
    },
    {
        "customer_id": "CUST-006",
        "first_name": "Sanjay",
        "last_name": "J",
        "email": "sanjay.j@example.com",
        "phone": "+91-9000000006",
        "company": "Pioneer Apps",
        "designation": "DevOps Engineer",
        "date_of_birth": "1996-09-08",
    },
    {
        "customer_id": "CUST-007",
        "first_name": "Pranika",
        "last_name": "S",
        "email": "pranika.s@example.com",
        "phone": "+91-9000000007",
        "company": "DataWorks Inc.",
        "designation": "Data Scientist",
        "date_of_birth": "1992-12-05",
    },
    {
        "customer_id": "CUST-008",
        "first_name": "Adhish",
        "last_name": "Krishnaa",
        "email": "adhish.krishnaa@example.com",
        "phone": "+91-9000000008",
        "company": "Cloudflare Systems",
        "designation": "Security Analyst",
        "date_of_birth": "1997-03-30",
    },
    {
        "customer_id": "CUST-009",
        "first_name": "Naren",
        "last_name": "G",
        "email": "naren.g@example.com",
        "phone": "+91-9000000009",
        "company": "Alpha Networks",
        "designation": "Network Engineer",
        "date_of_birth": "1991-10-18",
    },
    {
        "customer_id": "CUST-010",
        "first_name": "Kavin",
        "last_name": "G",
        "email": "kavin.g@example.com",
        "phone": "+91-9000000010",
        "company": "Beta Software",
        "designation": "Frontend Developer",
        "date_of_birth": "1998-01-22",
    },
    {
        "customer_id": "CUST-011",
        "first_name": "Pratip",
        "last_name": "TJ",
        "email": "pratip.tj@example.com",
        "phone": "+91-9000000011",
        "company": "Gamma Analytics",
        "designation": "Business Analyst",
        "date_of_birth": "1989-07-14",
    },
    {
        "customer_id": "CUST-012",
        "first_name": "Saumiyaa",
        "last_name": "Sri",
        "email": "saumiyaa.sri@example.com",
        "phone": "+91-9000000012",
        "company": "Delta Consultants",
        "designation": "HR Manager",
        "date_of_birth": "1995-11-11",
    },
    {
        "customer_id": "CUST-013",
        "first_name": "Theerdhana",
        "last_name": "AK",
        "email": "theerdhana.ak@example.com",
        "phone": "+91-9000000013",
        "company": "Epsilon Group",
        "designation": "Marketing Lead",
        "date_of_birth": "1994-04-04",
    },
    {
        "customer_id": "CUST-014",
        "first_name": "Soya",
        "last_name": "S",
        "email": "soya.s@example.com",
        "phone": "+91-9000000014",
        "company": "Zeta Ventures",
        "designation": "UX Designer",
        "date_of_birth": "1993-08-28",
    }
]

def seed_customers(db_session=None):
    db = db_session or SessionLocal()
    try:
        logger.info("Starting seed process for mock CRM customers...")
        for cust_data in DEMO_CUSTOMERS:
            # We copy it because we don't want to mutate the global dict if seed is called multiple times in tests
            cust_data_copy = cust_data.copy()
            customer_id = cust_data_copy.pop("customer_id")
            try:
                db_customer = service.get_customer_by_customer_id(db, customer_id)
                logger.info(f"Customer {customer_id} already exists. Safely updating demo fields.")
                for k, v in cust_data_copy.items():
                    setattr(db_customer, k, v)
                db.commit()
                logger.info(f"Customer {customer_id} updated.")
            except service.CustomerNotFoundError:
                new_customer = Customer(customer_id=customer_id, **cust_data_copy)
                db.add(new_customer)
                db.commit()
                logger.info(f"Created customer {customer_id}.")
        logger.info("Seed process completed successfully.")
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
    finally:
        if db_session is None:
            db.close()

DEMO_USERS = [
    {"name": "Sumathi P", "email": "sumathi.p@example.com", "role": Role.MANAGER},
    {"name": "Swathi Laxmi", "email": "swathi.laxmi@example.com", "role": Role.STAFF},
    {"name": "Karthikeyan VV", "email": "karthikeyan.vv@example.com", "role": Role.STAFF},
    {"name": "Mohana Kumar P", "email": "mohana.kumar@example.com", "role": Role.STAFF},
    {"name": "Sanjay J", "email": "sanjay.j@example.com", "role": Role.STAFF},
    {"name": "Pranika S", "email": "pranika.s@example.com", "role": Role.STAFF},
    {"name": "Adhish Krishnaa", "email": "adhish.krishnaa@example.com", "role": Role.STAFF},
    {"name": "Naren G", "email": "naren.g@example.com", "role": Role.STAFF},
    {"name": "Kavin G", "email": "kavin.g@example.com", "role": Role.STAFF},
    {"name": "Pratip TJ", "email": "pratip.tj@example.com", "role": Role.STAFF},
    {"name": "Saumiyaa Sri", "email": "saumiyaa.sri@example.com", "role": Role.STAFF},
    {"name": "Theerdhana AK", "email": "theerdhana.ak@example.com", "role": Role.STAFF},
    {"name": "Soya S", "email": "soya.s@example.com", "role": Role.STAFF},
]

def seed_users(db_session=None):
    db = db_session or SessionLocal()
    try:
        logger.info("Starting seed process for users and agents...")
        demo_password = os.environ.get("DEMO_PASSWORD", "demo123")
        hashed_password = get_password_hash(demo_password)
        
        # Admin bootstrap
        admin_email = os.environ.get("INITIAL_ADMIN_EMAIL", "admin@example.com")
        admin_name = os.environ.get("INITIAL_ADMIN_NAME", "Shelvaaathithyan VK")
        admin_pass = os.environ.get("INITIAL_ADMIN_PASSWORD", "admin123")
        
        users_to_seed = [{"name": admin_name, "email": admin_email, "role": Role.ADMIN, "hashed_password": get_password_hash(admin_pass)}]
        for u in DEMO_USERS:
            u_copy = u.copy()
            u_copy["hashed_password"] = hashed_password
            users_to_seed.append(u_copy)
            
        for u_data in users_to_seed:
            email = u_data["email"]
            db_user = db.query(User).filter(User.email == email).first()
            if db_user:
                logger.info(f"User {email} already exists.")
            else:
                db_user = User(
                    name=u_data["name"],
                    email=email,
                    password_hash=u_data["hashed_password"],
                    role=u_data["role"]
                )
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
                logger.info(f"Created user {email}.")
                
                # Create associated agent
                agent_id = f"agent-{u_data['name'].lower().replace(' ', '-')}-{uuid.uuid4().hex[:4]}"
                db_agent = Agent(
                    agent_id=agent_id,
                    user_id=db_user.id,
                    name=f"{u_data['name']} CRM Assistant"
                )
                db.add(db_agent)
                db.commit()
                logger.info(f"Created agent for {email}.")
        
        logger.info("User seed process completed successfully.")
    except Exception as e:
        logger.error(f"Error during user seeding: {e}")
        db.rollback()
    finally:
        if db_session is None:
            db.close()

if __name__ == "__main__":
    seed_users()
    seed_customers()
