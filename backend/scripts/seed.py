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
    },
    {
        "customer_id": "CUST-015",
        "first_name": "Arjun",
        "last_name": "R",
        "email": "arjun.r@example.com",
        "phone": "+91-9000000015",
        "company": "Nova Technologies",
        "designation": "Senior Software Engineer",
        "date_of_birth": "1990-05-15",
        "session_status": "ACTIVE"
    },
    {
        "customer_id": "CUST-016",
        "first_name": "Divya",
        "last_name": "M",
        "email": "divya.m@example.com",
        "phone": "+91-9000000016",
        "company": "Bright Systems",
        "designation": "Product Designer",
        "date_of_birth": "1992-07-22",
        "session_status": "ACTIVE"
    },
    {
        "customer_id": "CUST-017",
        "first_name": "Rahul",
        "last_name": "K",
        "email": "rahul.k@example.com",
        "phone": "+91-9000000017",
        "company": "Vertex Labs",
        "designation": "Engineering Manager",
        "date_of_birth": "1988-03-10",
        "session_status": "ACTIVE"
    },
    {
        "customer_id": "CUST-018",
        "first_name": "Meena",
        "last_name": "S",
        "email": "meena.s@example.com",
        "phone": "+91-9000000018",
        "company": "Orion Solutions",
        "designation": "Business Analyst",
        "date_of_birth": "1994-01-25",
        "session_status": "ACTIVE"
    },
    {
        "customer_id": "CUST-019",
        "first_name": "Vikram",
        "last_name": "P",
        "email": "vikram.p@example.com",
        "phone": "+91-9000000019",
        "company": "NextGen Networks",
        "designation": "DevOps Engineer",
        "date_of_birth": "1991-09-12",
        "session_status": "INACTIVE"
    },
    {
        "customer_id": "CUST-020",
        "first_name": "Ananya",
        "last_name": "R",
        "email": "ananya.r@example.com",
        "phone": "+91-9000000020",
        "company": "BluePeak Technologies",
        "designation": "UX Researcher",
        "date_of_birth": "1995-11-03",
        "session_status": "ACTIVE"
    },
    {
        "customer_id": "CUST-021",
        "first_name": "Suresh",
        "last_name": "V",
        "email": "suresh.v@example.com",
        "phone": "+91-9000000021",
        "company": "DataSphere Inc.",
        "designation": "Data Engineer",
        "date_of_birth": "1989-12-18",
        "session_status": "ACTIVE"
    },
    {
        "customer_id": "CUST-022",
        "first_name": "Priya",
        "last_name": "K",
        "email": "priya.k@example.com",
        "phone": "+91-9000000022",
        "company": "CloudNova",
        "designation": "HR Specialist",
        "date_of_birth": "1993-02-14",
        "session_status": "ACTIVE"
    },
    {
        "customer_id": "CUST-023",
        "first_name": "Akash",
        "last_name": "T",
        "email": "akash.t@example.com",
        "phone": "+91-9000000023",
        "company": "Alpha Digital",
        "designation": "Security Engineer",
        "date_of_birth": "1996-08-30",
        "session_status": "ACTIVE"
    },
    {
        "customer_id": "CUST-024",
        "first_name": "Kavya",
        "last_name": "N",
        "email": "kavya.n@example.com",
        "phone": "+91-9000000024",
        "company": "GreenTech Solutions",
        "designation": "Marketing Manager",
        "date_of_birth": "1990-06-05",
        "session_status": "INACTIVE"
    },
    {
        "customer_id": "CUST-025",
        "first_name": "Manoj",
        "last_name": "G",
        "email": "manoj.g@example.com",
        "phone": "+91-9000000025",
        "company": "Apex Consulting",
        "designation": "Solutions Architect",
        "date_of_birth": "1987-10-21",
        "session_status": "ACTIVE"
    },
    {
        "customer_id": "CUST-026",
        "first_name": "Harini",
        "last_name": "P",
        "email": "harini.p@example.com",
        "phone": "+91-9000000026",
        "company": "FinEdge Systems",
        "designation": "Finance Analyst",
        "date_of_birth": "1994-04-09",
        "session_status": "ACTIVE"
    },
    {
        "customer_id": "CUST-027",
        "first_name": "Dinesh",
        "last_name": "S",
        "email": "dinesh.s@example.com",
        "phone": "+91-9000000027",
        "company": "TechBridge",
        "designation": "QA Lead",
        "date_of_birth": "1992-01-11",
        "session_status": "ACTIVE"
    },
    {
        "customer_id": "CUST-028",
        "first_name": "Keerthana",
        "last_name": "V",
        "email": "keerthana.v@example.com",
        "phone": "+91-9000000028",
        "company": "InnovateWorks",
        "designation": "Project Manager",
        "date_of_birth": "1995-07-07",
        "session_status": "ACTIVE"
    },
    {
        "customer_id": "CUST-029",
        "first_name": "Naveen",
        "last_name": "J",
        "email": "naveen.j@example.com",
        "phone": "+91-9000000029",
        "company": "CoreStack Technologies",
        "designation": "Cloud Architect",
        "date_of_birth": "1989-11-28",
        "session_status": "ACTIVE"
    }
]

def clean_incorrect_customers(db):
    incorrect_emails = ["shelvaaathithyan.vk@example.com", "swathi.laxmi@example.com", "sumathi.p@example.com"]
    incorrect_ids = ["CUST-001", "CUST-002", "CUST-004"] # Example if CUST-004 was Sumathi
    
    customers_to_delete = db.query(Customer).filter(
        (Customer.email.in_(incorrect_emails)) | (Customer.customer_id.in_(incorrect_ids))
    ).all()
    
    for cust in customers_to_delete:
        logger.info(f"Removing incorrect CRM customer: {cust.email} ({cust.customer_id})")
        db.delete(cust)
    db.commit()

def seed_customers(db_session=None):
    db = db_session or SessionLocal()
    try:
        logger.info("Starting seed process for mock CRM customers...")
        clean_incorrect_customers(db)
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
                
        # Safely disable legacy staff portal users
        valid_emails = [u["email"] for u in users_to_seed]
        legacy_users = db.query(User).filter(User.email.notin_(valid_emails)).all()
        for l_user in legacy_users:
            if l_user.is_active:
                l_user.is_active = False
                logger.info(f"Disabled legacy portal user: {l_user.email}")
        db.commit()

        
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
