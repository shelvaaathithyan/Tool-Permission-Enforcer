import logging
from typing import Any, Dict
from sqlalchemy.orm import Session
from app.auth.models import User
from app.agent.models import Agent, Session as AgentSession, SessionStatus
from app.agent.schemas import AgentToolRequest
from app.crm import service as crm_service
from app.audit.service import log_audit_event, ActorType, AuditDecision, check_violation_threshold

logger = logging.getLogger(__name__)

class PermissionProxy:
    def __init__(self, db: Session):
        self.db = db

    def evaluate(self, request: AgentToolRequest, user: User, agent: Agent, session: AgentSession) -> dict:
        # 1 & 2. Validate Session Identity and Status
        if session.user_id != user.id or session.agent_id != agent.id or session.status != SessionStatus.ACTIVE:
            return self._block(request, user, agent, session, "Agent session is inactive or invalid.")

        # 3. Validate tool_name matches operation
        VALID_MAPPINGS = {
            "search_customers": {"operation": "READ", "resource": "CUSTOMER"},
            "get_customer": {"operation": "READ", "resource": "CUSTOMER"},
            "list_customers": {"operation": "READ", "resource": "CUSTOMER"},
            "create_customer": {"operation": "CREATE", "resource": "CUSTOMER"},
            "update_customer": {"operation": "UPDATE", "resource": "CUSTOMER"},
            "delete_customer": {"operation": "DELETE", "resource": "CUSTOMER"},
        }

        if request.tool_name not in VALID_MAPPINGS:
            return self._block(request, user, agent, session, "Invalid Agent tool definition.")
            
        mapping = VALID_MAPPINGS[request.tool_name]
        if request.operation != mapping["operation"] or request.resource != mapping["resource"]:
            return self._block(request, user, agent, session, "Invalid Agent tool definition.")

        # 4, 5, 6. Resolve customer for customer-specific requests
        customer_id_or_name = request.arguments.get("customer_id")
        if request.tool_name in ["get_customer", "update_customer", "delete_customer"]:
            if not customer_id_or_name:
                return self._block(request, user, agent, session, "Customer ID or name is required.")
                
            customer = None
            customer_str = str(customer_id_or_name)
            if customer_str.startswith("CUST-"):
                try:
                    customer = crm_service.get_customer_by_customer_id(self.db, customer_str)
                except crm_service.CustomerNotFoundError:
                    pass
            
            if not customer:
                # Try finding by name directly, or splitting it if not found
                customers = crm_service.search_customers(self.db, search_query=customer_str)
                if not customers:
                    parts = customer_str.split()
                    if parts:
                        customers = crm_service.search_customers(self.db, search_query=parts[0])
                if customers:
                    customer = customers[0]
            
            if not customer:
                return self._block(request, user, agent, session, "Customer could not be found.")
                
            request.arguments["customer_id"] = customer.customer_id
            
            if customer.session_status == "INACTIVE":
                return self._block(request, user, agent, session, "Customer session is INACTIVE.")

        # 7. If operation is CREATE/UPDATE/DELETE -> BLOCKED
        if request.operation in ["CREATE", "UPDATE", "DELETE"]:
            return self._block(request, user, agent, session, "Agent mutation operations are not permitted.")

        # 8 & 9. If operation is READ, execute CRM function and return ALLOWED
        if request.operation == "READ" and request.tool_name in ["get_customer", "search_customers", "list_customers"]:
            return self._allow_and_execute(request, user, agent, session)
            
        return self._block(request, user, agent, session, "Unknown operation.")

    def _block(self, request: AgentToolRequest, user: User, agent: Agent, session: AgentSession, reason: str) -> dict:
        log_audit_event(
            db=self.db,
            user_id=user.id,
            agent_id=agent.id,
            session_id=session.session_id,
            actor_type=ActorType.AGENT,
            operation=request.operation,
            resource=request.resource,
            tool_name=request.tool_name,
            customer_id=request.arguments.get("customer_id"),
            original_prompt=request.original_prompt,
            arguments=request.arguments,
            decision=AuditDecision.BLOCKED,
            reason=reason
        )
        
        if request.operation in ["CREATE", "UPDATE", "DELETE"]:
            check_violation_threshold(
                db=self.db,
                user_id=user.id,
                agent_id=agent.id,
                session_id=session.session_id
            )

        return {
            "decision": "BLOCKED",
            "reason": reason,
            "result": None
        }

    def _allow_and_execute(self, request: AgentToolRequest, user: User, agent: Agent, session: AgentSession) -> dict:
        result = None
        
        try:
            from app.crm.schemas import CustomerResponse
            if request.tool_name == "get_customer":
                customer = crm_service.get_customer_by_customer_id(self.db, request.arguments.get("customer_id"))
                result = CustomerResponse.model_validate(customer).model_dump(mode="json")
            elif request.tool_name == "list_customers":
                page = request.arguments.get("page", 1)
                page_size = request.arguments.get("page_size", 20)
                customers, total = crm_service.get_customers(self.db, page=page, page_size=page_size)
                items = [CustomerResponse.model_validate(c).model_dump(mode="json") for c in customers]
                result = {"items": items, "total": total, "page": page, "page_size": page_size}
            elif request.tool_name == "search_customers":
                query = request.arguments.get("query", "")
                customers = crm_service.search_customers(self.db, search_query=query)
                items = [CustomerResponse.model_validate(c).model_dump(mode="json") for c in customers]
                result = {"items": items, "total": len(items)}
        except crm_service.CustomerNotFoundError:
            result = {"error": "Customer not found."}
            reason = "Customer not found."
        except Exception as e:
            logger.error(f"CRM execution error: {e}")
            return self._block(request, user, agent, session, "CRM execution error.")

        # Log allowed execution
        reason = reason if 'reason' in locals() else "Security policy permitted this operation."
        log_audit_event(
            db=self.db,
            user_id=user.id,
            agent_id=agent.id,
            session_id=session.session_id,
            actor_type=ActorType.AGENT,
            operation=request.operation,
            resource=request.resource,
            tool_name=request.tool_name,
            customer_id=request.arguments.get("customer_id"),
            original_prompt=request.original_prompt,
            arguments=request.arguments,
            decision=AuditDecision.ALLOWED,
            reason=reason
        )

        return {
            "decision": "ALLOWED",
            "reason": reason,
            "result": result
        }

def get_permission_proxy(db: Session) -> PermissionProxy:
    return PermissionProxy(db)
