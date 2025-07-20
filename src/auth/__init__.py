"""
Authentication module initialization
"""

from .jwt_auth import jwt_auth, JWTAuth

__all__ = ['jwt_auth', 'JWTAuth']