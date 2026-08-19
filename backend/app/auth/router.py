from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.database.session import get_db
from app.auth import schemas, service, models
from app.core import security
from app.api import deps

router = APIRouter()

@router.post("/signup", response_model=schemas.SignupRequestResponse, status_code=status.HTTP_201_CREATED)
def signup(request_in: schemas.SignupRequestCreate, db: Session = Depends(get_db)):
    if request_in.requested_role == models.Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot signup as ADMIN")
        
    try:
        signup_req = service.create_signup_request(db, request_in)
        return signup_req
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = service.get_user_by_email(db, email=form_data.username)
    if not user:
        # Check if there is a pending or rejected signup request
        signup_req = service.get_signup_request_by_email(db, form_data.username)
        if signup_req:
            if signup_req.status == models.SignupStatus.PENDING:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account is awaiting administrator approval.")
            if signup_req.status == models.SignupStatus.REJECTED:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your registration request was rejected.")
                
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account has been disabled.")
        
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user

@router.post("/logout")
def logout():
    return {"message": "Successfully logged out"}
