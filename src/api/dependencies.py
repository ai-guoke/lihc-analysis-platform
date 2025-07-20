"""
API dependencies and utilities for LIHC Platform
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import secrets
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthManager:
    """Authentication and authorization manager"""
    
    def __init__(self):
        self.pwd_context = pwd_context
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

class RateLimiter:
    """Simple rate limiter for API endpoints"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        now = datetime.now()
        
        # Clean old entries
        self._cleanup_old_entries(now)
        
        # Check current requests
        if key not in self.requests:
            self.requests[key] = []
        
        # Count requests in current window
        window_start = now - timedelta(seconds=self.window_seconds)
        current_requests = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        if len(current_requests) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True
    
    def _cleanup_old_entries(self, now: datetime):
        """Clean up old entries to prevent memory leaks"""
        window_start = now - timedelta(seconds=self.window_seconds)
        
        for key in list(self.requests.keys()):
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > window_start
            ]
            
            if not self.requests[key]:
                del self.requests[key]

class TaskManager:
    """Background task management"""
    
    def __init__(self):
        self.tasks = {}
    
    def create_task(self, task_id: str, task_type: str, user_id: str, parameters: Dict[str, Any]):
        """Create a new task"""
        self.tasks[task_id] = {
            "task_id": task_id,
            "task_type": task_type,
            "user_id": user_id,
            "parameters": parameters,
            "status": "queued",
            "progress": 0.0,
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None,
            "error": None,
            "result": None
        }
    
    def update_task_status(self, task_id: str, status: str, progress: float = None, error: str = None):
        """Update task status"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task["status"] = status
        
        if progress is not None:
            task["progress"] = progress
        
        if error:
            task["error"] = error
        
        if status == "running" and task["started_at"] is None:
            task["started_at"] = datetime.now()
        
        if status in ["completed", "failed"]:
            task["completed_at"] = datetime.now()
        
        return True
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_user_tasks(self, user_id: str) -> list:
        """Get all tasks for a user"""
        return [task for task in self.tasks.values() if task["user_id"] == user_id]
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False

# Global instances
auth_manager = AuthManager()
rate_limiter = RateLimiter()
task_manager = TaskManager()