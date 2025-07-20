"""
JWT Authentication Module for LIHC Platform
Provides secure JSON Web Token authentication and authorization
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from passlib.context import CryptContext
import secrets

class JWTAuth:
    """JWT Authentication manager"""
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        if not self.secret_key:
            # Generate a secure secret key if not provided
            self.secret_key = secrets.token_urlsafe(64)
            print("⚠️ WARNING: JWT_SECRET_KEY not set in environment. Using temporary key.")
            print("For production, set JWT_SECRET_KEY environment variable!")
        
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.expiration_hours = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create a new JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=self.expiration_hours)
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token creation failed: {str(e)}"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_user_token(self, user_id: str, username: str, role: str) -> str:
        """Create a token for a specific user"""
        token_data = {
            "sub": user_id,
            "username": username,
            "role": role,
            "type": "access_token"
        }
        return self.create_access_token(token_data)
    
    def get_user_from_token(self, token: str) -> Dict[str, str]:
        """Extract user information from token"""
        payload = self.verify_token(token)
        
        user_id = payload.get("sub")
        username = payload.get("username")
        role = payload.get("role")
        
        if not all([user_id, username, role]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return {
            "user_id": user_id,
            "username": username,
            "role": role
        }

# Global JWT authentication instance
jwt_auth = JWTAuth()