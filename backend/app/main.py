from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.crm.router import router as crm_router
from app.audit.router import router as audit_router
from app.auth.router import router as auth_router
from app.agent.router import router as agent_router
from app.admin.router import router as admin_router

app = FastAPI(
    title="Tool Permission Enforcer",
    description="Tool Permission Enforcer API",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crm_router, prefix="/api/v1/crm/customers", tags=["crm"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(agent_router, prefix="/api/v1/agent", tags=["agent"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(audit_router, prefix="/api/v1/audit", tags=["audit"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}
