from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.crm.router import router as crm_router
from app.auth.router import router as auth_router
from app.agent.router import router as agent_router

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

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(agent_router, prefix="/api/v1/agent", tags=["Agent"])
app.include_router(crm_router, prefix="/api/v1/crm/customers", tags=["CRM"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}
