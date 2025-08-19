from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Request, Form
from fastapi.responses import JSONResponse
from sqlalchemy import select
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from schema.forms import LoginForm, SignupForm
from schema.models import User
from database.database import get_db
from utils.utils import get_current_user
from utils.security import verify_password, hash_password
from utils.jwt_handler import create_access_token




router = APIRouter()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=["*"],
)

app.include_router(router, prefix="/auth", tags=["auth"])



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
async def login(form_data: LoginForm, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}




