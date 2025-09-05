from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app import schemas
from app.db.base import SessionLocal
from app.core.security import create_access_token, get_password_hash, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from app.crud.user import get_user_by_email as crud_get_user_by_email, create_user as crud_create_user, authenticate_user as crud_authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
async def register(
    request: Request,
    db: Session = Depends(get_db)
):
    form_data = await request.form()
    email = form_data.get('email')
    password = form_data.get('password')
    
    if not email or not password:
        return JSONResponse(
            status_code=400,
            content={"detail": "Email and password are required"}
        )
        
    try:
        user_in = schemas.user.UserCreate(email=email, password=password)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"detail": str(e)}
        )
    """
    Register a new user.
    """
    try:
        print(f"Attempting to register user with email: {user_in.email}")
        
        # Check if user already exists
        db_user = crud_get_user_by_email(db, email=user_in.email)
        if db_user:
            print(f"User with email {user_in.email} already exists")
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        print("Creating new user...")
        # Create new user
        try:
            user = crud_create_user(db=db, email=user_in.email, password=user_in.password)
            print(f"User created successfully: {user.email}")
            return user
        except Exception as e:
            print(f"Error in create_user: {str(e)}")
            db.rollback()
            raise
            
    except HTTPException as he:
        print(f"HTTPException: {str(he)}")
        raise
    except Exception as e:
        error_msg = f"Unexpected error creating user: {str(e)}"
        print(error_msg)
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

@router.post("/login")
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        form_data = await request.form()
        username = form_data.get('username')
        password = form_data.get('password')
        
        if not username or not password:
            return JSONResponse(
                status_code=400,
                content={"detail": "Email and password are required"}
            )
            
        user = crud_authenticate_user(db, email=username, password=password)
        
        if not user:
            return JSONResponse(
                status_code=401,
                content={"detail": "Incorrect email or password"}
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, 
            expires_delta=access_token_expires
        )
        
        # Return user data along with the token
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": {
                "email": user.email,
                "is_active": user.is_active,
                "id": user.id
            }
        }
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An error occurred during login"}
        )
