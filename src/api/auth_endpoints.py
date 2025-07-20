"""
Authentication endpoints for LIHC Platform
Provides login, logout, and token management
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
import os

from src.auth.jwt_auth import jwt_auth
from src.database.models import User, SessionLocal
from src.utils.logging_system import LIHCLogger

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = LIHCLogger(name="AuthAPI")

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Authenticate user and return JWT token"""
    db = SessionLocal()
    try:
        # Find user by username
        user = db.query(User).filter(User.username == login_data.username).first()
        
        if not user:
            logger.warning(f"Login attempt with non-existent username: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        if not user.is_active:
            logger.warning(f"Login attempt with inactive user: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Verify password
        if not jwt_auth.verify_password(login_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create JWT token
        access_token = jwt_auth.create_user_token(
            user_id=str(user.id),
            username=user.username,
            role=user.role
        )
        
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.commit()
        
        logger.info(f"Successful login for user: {user.username}")
        
        return LoginResponse(
            access_token=access_token,
            user_id=str(user.id),
            username=user.username,
            role=user.role
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    finally:
        db.close()

@router.post("/register", response_model=LoginResponse)
async def register(user_data: UserCreate):
    """Register a new user (if registration is enabled)"""
    # Check if registration is enabled
    allow_registration = os.getenv("ALLOW_REGISTRATION", "false").lower() == "true"
    if not allow_registration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User registration is disabled"
        )
    
    db = SessionLocal()
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = jwt_auth.hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role="user",  # Default role
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create JWT token
        access_token = jwt_auth.create_user_token(
            user_id=str(new_user.id),
            username=new_user.username,
            role=new_user.role
        )
        
        logger.info(f"New user registered: {new_user.username}")
        
        return LoginResponse(
            access_token=access_token,
            user_id=str(new_user.id),
            username=new_user.username,
            role=new_user.role
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )
    finally:
        db.close()

@router.post("/logout")
async def logout():
    """Logout user (client should discard token)"""
    # In a stateless JWT system, logout is handled client-side
    # The client should simply discard the token
    # For added security, you could implement a token blacklist
    return {"message": "Successfully logged out"}