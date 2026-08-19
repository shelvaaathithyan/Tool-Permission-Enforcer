from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.api import deps
from app.audit import service, schemas

router = APIRouter()

@router.get("/logs", response_model=List[schemas.AuditLogResponse])
def get_audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user = Depends(deps.require_admin)
):
    return service.get_audit_logs(db, limit, offset)

@router.get("/alerts", response_model=List[schemas.SecurityAlertResponse])
def get_security_alerts(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user = Depends(deps.require_admin)
):
    return service.get_security_alerts(db, limit, offset)
