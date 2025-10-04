import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import EmailStr
from pydantic.main import BaseModel
import jwt

security = HTTPBearer(auto_error=False)
SECRET_KEY = os.environ.get("SECRET_KEY", "mysecret")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with an expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm='HS256')

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Verify the JWT token from the Authorization header."""

    if credentials is None:
        return None
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_token_dependency(config: Dict):
    """Return the token dependency if JWT is enabled, else a function that returns None."""

    if config.get("security", {}).get("jwt_enabled", False):
        return verify_token
    else:
        return lambda: None


class TokenRequest(BaseModel):
    email: EmailStr