# tests/test_security.py
import pytest
from services.security_manager import SecurityManager, SecurityException

def test_jwt_generation():
    """Test JWT token generation"""
    security = SecurityManager()
    token = security.generate_token("test_user", "analyst")
    assert token is not None
    assert len(token) > 50

def test_jwt_validation():
    """Test JWT token validation"""
    security = SecurityManager()
    token = security.generate_token("test_user", "analyst")
    payload = security.validate_token(token)
    assert payload['user_id'] == "test_user"
    assert payload['role'] == "analyst"

def test_input_sanitization():
    """Test input sanitization"""
    security = SecurityManager()
    
    dangerous_input = "<script>alert('xss')</script>"
    sanitized = security.sanitize_input(dangerous_input)
    
    assert "<script>" not in sanitized
    assert "alert" in sanitized  # Text remains, tags removed

def test_sensitive_data_hashing():
    """Test PII hashing"""
    security = SecurityManager()
    
    email = "user@example.com"
    hashed = security.hash_sensitive_data(email)
    
    assert hashed != email
    assert len(hashed) == 64  # SHA-256 hex length
    
    # Same input = same hash
    assert security.hash_sensitive_data(email) == hashed

def test_rate_limiting():
    """Test rate limiting"""
    security = SecurityManager()
    
    user_id = "test_user"
    
    # Should pass for first 100 requests
    for i in range(100):
        assert security.check_rate_limit(user_id, max_requests=100) == True
    
    # 101st request should fail
    with pytest.raises(SecurityException):
        security.check_rate_limit(user_id, max_requests=100)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])