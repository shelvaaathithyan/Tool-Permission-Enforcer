import os
import sys
import logging

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from app.database.session import SessionLocal
from app.auth.models import User
from app.agent.models import Agent
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL = "ravi.s@example.com"
NEW_PASSWORD = "demo123"

def reset_ravi_password():
    db = SessionLocal()

    try:
        logger.info("Checking whether %s exists...", EMAIL)

        existing_user = (
            db.query(User)
            .filter(User.email == EMAIL)
            .first()
        )

        if not existing_user:
            logger.info("User %s does NOT exist. Stopping and making no changes.", EMAIL)
            return

        logger.info("User %s exists. Resetting password...", EMAIL)

        # Safely hash the new password using the app's standard function
        new_password_hash = get_password_hash(NEW_PASSWORD)
        
        # Update ONLY the password_hash field
        existing_user.password_hash = new_password_hash
        
        # Commit the transaction safely
        db.commit()

        logger.info("Successfully reset password for %s.", EMAIL)
        logger.info("All other fields (name, role, is_active, agents, customers) remain untouched.")

    except Exception as exc:
        db.rollback()
        logger.exception("Password reset failed. Transaction rolled back: %s", exc)
        raise

    finally:
        db.close()

if __name__ == "__main__":
    reset_ravi_password()
