import os
from datetime import datetime, timedelta
from typing import Optional, List

from jose import jwt, JWTError
from passlib.context import CryptContext

# Şifreleme Kütüphanesi
from cryptography.fernet import Fernet

# =====================
# CONFIG
# =====================

SECRET_KEY = "CHANGE_THIS_SECRET_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Veri Şifreleme Anahtarı (Encryption Key)
# Gerçek projede .env dosyasından okunmalı.
# Demo için sabit bir key kullanıyoruz ki server kapanıp açılınca veriler bozulmasın.
# (Fernet key 32 url-safe base64-encoded bytes olmalı)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "J_check_this_is_32_bytes_key_for_demo_purposes_only=") 
# Eğer key hatası alırsan terminalde şu komutla yeni key üretip buraya yapıştırabilirsin:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

try:
    cipher_suite = Fernet(ENCRYPTION_KEY)
except Exception as e:
    print(f"Encryption Key Error: {e}. Generating a temporary one (Warning: Data persistence issues may occur).")
    cipher_suite = Fernet(Fernet.generate_key())

# =====================
# PASSWORD HASHING
# =====================

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# =====================
# DATA ENCRYPTION
# =====================

def encrypt_data(data: str) -> str:
    """Hassas veriyi veritabanına kaydetmeden önce şifreler."""
    if not data:
        return None
    try:
        return cipher_suite.encrypt(data.encode("utf-8")).decode("utf-8")
    except Exception as e:
        print(f"Encryption Error: {e}")
        return data  # Hata olursa veriyi olduğu gibi döndür (Fallback)


def decrypt_data(token: str) -> str:
    """Veritabanından okunan şifreli veriyi çözer."""
    if not token:
        return None
    try:
        return cipher_suite.decrypt(token.encode("utf-8")).decode("utf-8")
    except Exception:
        # Şifre çözülemezse (örn: key değiştiyse veya veri şifresizse) ham hâlini göster
        return "[Encrypted Data]"


# =====================
# JWT TOKEN
# =====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return payload

def require_roles(allowed_roles: List[str]):
    def role_checker(user_payload: dict = Depends(get_current_user)):
        user_role = user_payload.get("role")

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return user_payload

    return role_checker

import hashlib


def generate_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
