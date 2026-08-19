import os
import sys
import logging

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from app.database.session import SessionLocal
from app.auth.models import User, Role
from app.agent.models import Agent
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


EMAIL = "ravi.s@example.com"
PASSWORD = "demo123"
AGENT_ID = "agent-ravi-001"
AGENT_NAME = "Ravi S CRM Assistant"
USER_NAME = "Ravi S"


def create_ravi():
    db = SessionLocal()

    try:
        logger.info("Checking whether %s already exists...", EMAIL)

        existing_user = (
            db.query(User)
            .filter(User.email == EMAIL)
            .first()
        )

        if existing_user:
            logger.info(
                "User %s already exists. Nothing will be changed.",
                EMAIL,
            )
            return

        logger.info("User does not exist. Creating user...")

        password_hash = get_password_hash(PASSWORD)

        new_user = User(
            name=USER_NAME,
            email=EMAIL,
            password_hash=password_hash,
            role=Role.STAFF,
            is_active=True,
        )

        db.add(new_user)
        db.flush()

        logger.info("Creating agent record...")

        new_agent = Agent(
            agent_id=AGENT_ID,
            user_id=new_user.id,
            name=AGENT_NAME,
            is_active=True,
        )

        db.add(new_agent)

        db.commit()

        logger.info("Successfully created %s", EMAIL)
        logger.info("User ID: %s", new_user.id)

    except Exception as exc:
        db.rollback()
        logger.exception(
            "Creation failed. Transaction rolled back: %s",
            exc,
        )
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_ravi()
