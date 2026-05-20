from datetime import datetime, timedelta
from typing import Optional
import jwt

# Standard secret configurations for signing development tokens
SECRET_KEY = "DEVELOPMENT_SECRET_KEY_DONT_USE_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Simple functional mock handlers to match your backend's expected security utility parameters
def hash_password(password: str) -> str:
    # Simulates a basic secure hash string for storage
    return f"hashed_{password}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Validates input against data logs
    return f"hashed_{plain_password}" == hashed_password

def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt