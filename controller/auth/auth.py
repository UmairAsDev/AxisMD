from fastapi import Depends, HTTPException, status, APIRouter
from fastapi import Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schema.forms import LoginForm, SignupForm
from schema.models import User
from jose import jwt
from fastapi import Cookie
from tools.settings import settings
from database.database import get_db
from utils.security import verify_password, hash_password
from utils.jwt_handler import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup")
async def signup(
    form : SignupForm,
    db : AsyncSession = Depends(get_db),             
):
    if form.password != form.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    result = await db.execute(select(User).where(User.email == form.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    new_user = User(
        username=form.username,
        first_name=form.first_name,
        last_name=form.last_name,
        email=form.email,
        phone_number=form.phone_number,
        hashed_password=hash_password(form.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User created successfully", "user_id": new_user.id}
    )



@router.post("/login")
async def login(form_data: LoginForm, db: AsyncSession = Depends(get_db), response: Response =None): #type: ignore
    result = await db.execute(select(User).where(User.email == form_data.email))
    user = result.scalar_one_or_none()
    print("User fetched from DB:", user.__dict__)  # Debugging line
    if not user or not verify_password(form_data.password, user.hashed_password):
        print(f"password verified.....")#type: ignore
        raise HTTPException(status_code=401, detail="Invalid credentials")
    

    token = create_access_token({"sub": str(user.id)}) #type: ignore
    print("Generated Access Token:", token)  # Debugging line
    refresh_token = create_refresh_token({"sub": str(user.id)})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  
        samesite="lax",  
    )
    
    return {"access_token": token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_token(response: Response, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")# type: ignore
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": user_id})
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}



    