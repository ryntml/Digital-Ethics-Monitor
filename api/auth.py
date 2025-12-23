# api/auth.py
from functools import wraps
from flask import request, jsonify
from services.security_manager import SecurityManager, SecurityException

security_manager = SecurityManager()

def require_auth(f):
    """Decorator for JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.replace('Bearer ', '')
        
        try:
            user_info = security_manager.validate_token(token)
            request.user = user_info
            return f(*args, **kwargs)
        except SecurityException as e:
            return jsonify({"error": str(e)}), 401
    
    return decorated

def require_role(role: str):
    """Decorator for role-based access control"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                security_manager.check_permission(request.user.get('role'), role)
                return f(*args, **kwargs)
            except SecurityException as e:
                return jsonify({"error": str(e)}), 403
        return decorated
    return decorator