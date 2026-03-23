from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from typing import List
from app.core.config import settings
from app.core.security import ALGORITHM
from app.models.user import UserResponse, RoleEnum
from app.db.mongodb import get_database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_database)) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if not settings.JWT_SECRET_KEY:
            raise credentials_exception
            
        payload = jwt.decode(token, settings.JWT_SECRET_KEY.get_secret_value(), algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user_dict = await db["users"].find_one({"email": email})
    
    if user_dict is None:
        raise credentials_exception
    
    user_dict["id"] = str(user_dict["_id"])
    return UserResponse(**user_dict)

def require_role(required_roles: List[RoleEnum]):
    def role_checker(current_user: UserResponse = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires roles: {[r.value for r in required_roles]}"
            )
        return current_user
    return role_checker
