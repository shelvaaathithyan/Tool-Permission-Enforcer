from sqlalchemy.orm import Session as DBSession
from app.auth.models import User
from app.agent.models import Agent, Session as AgentSession, SessionStatus
from app.agent.llm.base import LLMProvider
from app.agent.tool_registry import registry
from app.agent.schemas import AgentToolRequest, AgentInvokeResponse
from app.audit.service import log_audit_event, ActorType, AuditDecision
import logging

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def invoke(self, db: DBSession, user: User, agent: Agent, active_session: AgentSession, prompt: str) -> AgentInvokeResponse:
        # Validate active session
        if active_session.status != SessionStatus.ACTIVE:
            raise ValueError("Session is inactive")
            
        if active_session.user_id != user.id or active_session.agent_id != agent.id:
            raise ValueError("Session ownership mismatch")

        # Get tools and invoke LLM
        tools = registry.get_all_tools()
        
        try:
            nl_response, tool_call = self.llm_provider.generate_response(prompt, tools)
        except Exception as e:
            logger.error(f"LLM Provider error: {e}")
            raise RuntimeError("Failed to process agent request via LLM")

        if not tool_call:
            return AgentInvokeResponse(
                status="COMPLETED",
                response=nl_response or "I couldn't identify a tool to fulfill that request.",
                tool_request=None
            )

        tool_name = tool_call["name"]
        arguments = tool_call["arguments"]

        # Validate tool
        if not registry.validate_tool_call(tool_name):
            raise ValueError(f"LLM selected unknown tool: {tool_name}")

        validation_errors = registry.validate_tool_arguments(tool_name, arguments)
        if validation_errors:
            error_reason = f"Malformed tool arguments: {', '.join(validation_errors)}"
            logger.warning(f"Agent validation error: {error_reason}")
            return AgentInvokeResponse(
                status="ERROR",
                decision="ERROR",
                reason=error_reason,
                response="I encountered an error understanding the parameters for this request.",
                tool_request=AgentToolRequest(
                    tool_name=tool_name,
                    operation=registry.get_tool_metadata(tool_name)["operation"],
                    resource=registry.get_tool_metadata(tool_name)["resource"],
                    arguments=arguments,
                    original_prompt=prompt
                ),
                result={"error": error_reason}
            )

        metadata = registry.get_tool_metadata(tool_name)
        
        tool_req = AgentToolRequest(
            tool_name=tool_name,
            operation=metadata["operation"],
            resource=metadata["resource"],
            arguments=arguments,
            original_prompt=prompt
        )

        customer_id = arguments.get("customer_id")

        from app.permission_proxy.service import get_permission_proxy
        proxy = get_permission_proxy(db)
        evaluation = proxy.evaluate(tool_req, user, agent, active_session)

        status_value = "ALLOWED" if evaluation["decision"] == "ALLOWED" else "BLOCKED"
        response_msg = (
            f"I understood this as a {tool_req.operation} request. Result: ALLOWED." 
            if status_value == "ALLOWED" 
            else "Security policy blocked this Agent operation."
        )

        return AgentInvokeResponse(
            status=status_value,
            decision=evaluation["decision"],
            reason=evaluation.get("reason"),
            result=evaluation.get("result"),
            response=response_msg,
            tool_request=tool_req
        )
