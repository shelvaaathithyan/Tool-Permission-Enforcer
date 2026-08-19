from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.auth.models import User, Role
from app.auth import service as auth_service
from app.agent.models import Agent

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = auth_service.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user

def require_authenticated_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user

def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user

def require_user_portal_access(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    # Managers and Staff use the user portal.
    return current_user

def get_current_agent(current_user: Annotated[User, Depends(get_current_user)]) -> Agent:
    if not current_user.agent:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User has no associated agent")
    return current_user.agent
