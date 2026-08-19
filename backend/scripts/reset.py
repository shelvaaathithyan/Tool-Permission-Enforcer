import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.session import SessionLocal
from app.crm.models import Customer
from app.auth.models import User, Role
from app.agent.models import Agent
from app.core.security import get_password_hash
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def reset_and_seed():
    db = SessionLocal()
    try:
        from app.audit.models import AuditLog, SecurityAlert
        from app.agent.models import Session
        
        logger.info("Deleting existing demo customers...")
        db.query(Customer).delete()
        db.commit()

        # Use the existing admin user to avoid unique constraint violation
        pwd = get_password_hash("demo123")
        admin_data = AGENTS[-1] # System Administrator
        
        admin_user = db.query(User).filter(User.email == admin_data[5]).first()
        if not admin_user:
            admin_user = User(email=admin_data[5], password_hash=pwd, role=admin_data[3])
            db.add(admin_user)
            db.flush()
            
        admin_user.name = admin_data[2]
        admin_user.password_hash = pwd
        admin_user.role = admin_data[3]
        admin_user.is_active = True
        db.flush()
        
        admin_agent = db.query(Agent).filter(Agent.user_id == admin_user.id).first()
        if not admin_agent:
            admin_agent = Agent(user_id=admin_user.id)
            db.add(admin_agent)
            db.flush()
            
        admin_agent.agent_id = admin_data[0]
        admin_agent.name = admin_data[1]
        admin_agent.is_active = True
        db.flush()

        logger.info("Reassigning existing sessions and audit logs to the new Admin...")
        db.query(Session).filter(Session.agent_id != admin_agent.id).update({"user_id": admin_user.id, "agent_id": admin_agent.id})
        db.query(AuditLog).filter(AuditLog.agent_id != admin_agent.id).update({"user_id": admin_user.id, "agent_id": admin_agent.id})
        db.query(SecurityAlert).filter(SecurityAlert.agent_id != admin_agent.id).update({"user_id": admin_user.id, "agent_id": admin_agent.id})
        db.query(SecurityAlert).filter(SecurityAlert.resolved_by.isnot(None), SecurityAlert.resolved_by != admin_user.id).update({"resolved_by": admin_user.id})
        db.commit()

        logger.info("Deleting old agents and users...")
        db.query(Agent).filter(Agent.id != admin_agent.id).delete()
        db.query(User).filter(User.id != admin_user.id).delete()
        db.commit()

        logger.info("Inserting 20 new customers...")
        for cid, fname, lname, comp, desig, email, status in CUSTOMERS:
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
        
        logger.info("Inserting the remaining 9 new agents/users...")
        for aid, aname, uname, urole, status, email in AGENTS[:-1]:
            u = User(
                name=uname,
                email=email,
                password_hash=pwd,
                role=urole,
                is_active=(status == "ACTIVE")
            )
            db.add(u)
            db.flush()
            
            a = Agent(
                agent_id=aid,
                user_id=u.id,
                name=aname,
                is_active=(status == "ACTIVE")
            )
            db.add(a)
            
        db.commit()
        logger.info("Reset complete!")
    except Exception as e:
        db.rollback()
        logger.error(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed()

