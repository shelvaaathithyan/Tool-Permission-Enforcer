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

        metadata = registry.get_tool_metadata(tool_name)
        
        tool_req = AgentToolRequest(
            tool_name=tool_name,
            operation=metadata["operation"],
            resource=metadata["resource"],
            arguments=arguments,
            original_prompt=prompt
        )

        customer_id = arguments.get("customer_id")

        # Create Audit Log
        log_audit_event(
            db=db,
            user_id=user.id,
            agent_id=agent.id,
            session_id=active_session.session_id,
            actor_type=ActorType.AGENT,
            operation=tool_req.operation,
            resource=tool_req.resource,
            tool_name=tool_req.tool_name,
            customer_id=customer_id,
            original_prompt=prompt,
            arguments=arguments,
            decision=AuditDecision.PENDING
        )

        return AgentInvokeResponse(
            status="PENDING_PERMISSION_PROXY",
            response=f"I understood this as a {tool_req.operation} request.",
            tool_request=tool_req
        )
