import hashlib
import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
import json

class SecurityException(Exception):
    """Custom exception for security violations."""
    pass

class SecurityManager:
    """13 Security Rules Implementation"""
    
    def __init__(self, secret_key: str = None):
        # Environment variable'dan secret key al
        import os
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-me')
        self.rate_limit_store = {}
        self.audit_log = []
        
        # Configure secure logging
        Path('logs').mkdir(exist_ok=True)
        logging.basicConfig(
            filename='logs/security_audit.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)