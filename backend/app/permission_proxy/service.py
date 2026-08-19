import logging
from sqlalchemy.orm import Session
from app.agent.models import Agent
from app.crm import service as crm_service

logger = logging.getLogger(__name__)

class PermissionProxy:
    def __init__(self, db: Session):
        self.db = db

    def invoke(self, agent: Agent, session_id: str, tool_name: str, operation: str, arguments: dict):
        logger.info(f"PermissionProxy intercepted tool call from {agent.agent_id} in session {session_id}")
        logger.info(f"Tool: {tool_name}, Operation: {operation}, Arguments: {arguments}")
        
        if tool_name == "crm":
            if operation == "read":
                customer_id = arguments.get("customer_id")
                if customer_id:
                    return crm_service.get_customer_by_customer_id(self.db, customer_id)
                else:
                    return {"error": "Missing customer_id"}
            elif operation == "list":
                page = arguments.get("page", 1)
                page_size = arguments.get("page_size", 20)
                customers, total = crm_service.get_customers(self.db, page=page, page_size=page_size)
                return {"items": customers, "total": total}
            return {"status": "success", "message": f"Proxy allowed {operation}"}
        
        return {"error": f"Unknown tool {tool_name}"}

def get_permission_proxy(db: Session) -> PermissionProxy:
    return PermissionProxy(db)
