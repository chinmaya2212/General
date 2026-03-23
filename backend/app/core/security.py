from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
import bcrypt
import jwt
import logging
from fastapi import Request
from app.core.config import settings

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    if not settings.JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY is not configured.")

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=ALGORITHM)
    return encoded_jwt

def audit_log(request: Request, action: str, user_id: str, status: str = "success", details: str = ""):
    """
    Helper function to write an audit log for sensitive endpoints.
    """
    ip_address = request.client.host if request.client else "unknown"
    logger.info(
        f"AUDIT_LOG | action={action} | user={user_id} | "
        f"status={status} | ip={ip_address} | details={details}"
    )

# --- Auth Dependency Scaffolding ---
def get_current_user():
    """
    Scaffolding function to be used via Depends() in endpoints.
    e.g., @router.get('/secure', dependencies=[Depends(get_current_user)])
    """
    pass
