import hashlib
import jwt
import logging
import re
import html
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
import os


class SecurityException(Exception):
    """Custom exception for security violations."""
    pass


class SecurityManager:
    """13 Security Rules Implementation"""
    
    def __init__(self, secret_key: str = None):
        # Environment variable'dan secret key al
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-me')
        self.rate_limit_store: Dict[str, list] = {}
        self.audit_log = []
        
        # Configure secure logging
        Path('logs').mkdir(exist_ok=True)
        logging.basicConfig(
            filename='logs/security_audit.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def generate_token(self, user_id: str, role: str = "user") -> str:
        """
        Generate a JWT token for authentication.
        
        Args:
            user_id: Unique identifier for the user
            role: User role (admin, analyst, viewer, user)
            
        Returns:
            JWT token string
        """
        payload = {
            "user_id": user_id,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        self.logger.info(f"Token generated for user: {user_id}")
        
        return token

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a JWT token and return payload.
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload dictionary
            
        Raises:
            SecurityException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            self.logger.info(f"Token validated for user: {payload.get('user_id')}")
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token validation failed: Token expired")
            raise SecurityException("Token has expired")
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Token validation failed: {str(e)}")
            raise SecurityException(f"Invalid token: {str(e)}")

    def sanitize_input(self, text: str) -> str:
        """
        Sanitize user input to prevent XSS attacks.
        Removes HTML/script tags while preserving text content.
        
        Args:
            text: Raw user input
            
        Returns:
            Sanitized text string
        """
        if not text:
            return ""
        
        # Remove script tags and their content
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove other HTML tags but keep content
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        return text.strip()

    def hash_sensitive_data(self, data: str) -> str:
        """
        Hash sensitive data (PII) using SHA-256.
        
        Args:
            data: Sensitive data to hash
            
        Returns:
            SHA-256 hex digest (64 characters)
        """
        if not data:
            return ""
        
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def check_rate_limit(self, user_id: str, max_requests: int = 100, window_seconds: int = 3600) -> bool:
        """
        Check if user has exceeded rate limit.
        
        Args:
            user_id: User identifier
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            True if within limit
            
        Raises:
            SecurityException: If rate limit exceeded
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Initialize user's request history if not exists
        if user_id not in self.rate_limit_store:
            self.rate_limit_store[user_id] = []
        
        # Clean old entries outside the window
        self.rate_limit_store[user_id] = [
            ts for ts in self.rate_limit_store[user_id] 
            if ts > window_start
        ]
        
        # Check if limit exceeded
        if len(self.rate_limit_store[user_id]) >= max_requests:
            self.logger.warning(f"Rate limit exceeded for user: {user_id}")
            raise SecurityException(f"Rate limit exceeded. Max {max_requests} requests per {window_seconds} seconds.")
        
        # Record this request
        self.rate_limit_store[user_id].append(now)
        
        return True

    def log_audit_event(self, event_type: str, user_id: str, details: str) -> Dict[str, Any]:
        """
        Log a security audit event.
        
        Args:
            event_type: Type of event (LOGIN, LOGOUT, ACCESS, etc.)
            user_id: User who triggered the event
            details: Event details
            
        Returns:
            Audit log entry
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details,
            "hash": self.hash_sensitive_data(f"{event_type}{user_id}{details}")
        }
        
        self.audit_log.append(entry)
        self.logger.info(f"AUDIT: {event_type} - User: {user_id} - {details}")
        
        return entry

    def get_audit_logs(self, limit: int = 100) -> list:
        """
        Retrieve recent audit logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of audit log entries
        """
        return self.audit_log[-limit:]