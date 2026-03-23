from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password, get_password_hash, create_access_token, audit_log
from app.models.user import UserCreate, UserInDB, UserResponse, Token, RoleEnum
from app.db.mongodb import get_database
from app.api.v1.dependencies import get_current_user, require_role

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_database)):
    user_dict = await db["users"].find_one({"email": form_data.username})
    if not user_dict or not verify_password(form_data.password, user_dict["hashed_password"]):
        audit_log(request, "login", form_data.username, "failure", "Invalid credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    audit_log(request, "login", form_data.username, "success")
    access_token = create_access_token(subject=user_dict["email"])
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@router.post("/seed-admin", response_model=UserResponse)
async def seed_admin(user_in: UserCreate, request: Request, db = Depends(get_database)):
    """Local demo setup endpoint."""
    existing_admin = await db["users"].find_one({"role": RoleEnum.admin.value})
    if existing_admin:
        audit_log(request, "seed-admin", user_in.email, "failure", "Admin already exists")
        raise HTTPException(status_code=400, detail="Admin user already seeded.")

    user_dict = await db["users"].find_one({"email": user_in.email})
    if user_dict:
        raise HTTPException(status_code=400, detail="Email already registered.")
        
    hashed_password = get_password_hash(user_in.password)
    user_db = UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
    user_db.role = RoleEnum.admin
    
    new_user = await db["users"].insert_one(user_db.model_dump())
    
    response_usr = user_db.model_dump()
    response_usr["id"] = str(new_user.inserted_id)
    audit_log(request, "seed-admin", user_in.email, "success", f"Created admin {response_usr['id']}")
    return UserResponse(**response_usr)

@router.get("/admin-only", dependencies=[Depends(require_role([RoleEnum.admin]))])
async def admin_only_test():
    return {"message": "You are a confirmed admin."}
