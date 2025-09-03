from fastapi import Depends, HTTPException, status, APIRouter
from fastapi_mail import MessageSchema, ConnectionConfig, FastMail
from starlette.background import BackgroundTasks
from fastapi import Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schema.forms import LoginForm, SignupForm
from pydantic import SecretStr, BaseModel
from schema.models import User
from jose import jwt
from fastapi_mail import MessageSchema, MessageType
from fastapi import Cookie
from tools.settings import settings
from database.database import get_db
from utils.security import verify_password, hash_password
from utils.jwt_handler import create_access_token, create_refresh_token
from datetime import datetime, timedelta
from utils.security import create_reset_token, verify_reset_token



conf = ConnectionConfig(
    MAIL_USERNAME="harrydoe@gmail.com",
    MAIL_PASSWORD=SecretStr("harry123"), 
    MAIL_FROM="your_email@gmail.com",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


fm = FastMail(config=conf)

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
    if not user or not verify_password(form_data.password, user.hashed_password):#type:ignore
        print(f"password verified.....")#type: ignore
        raise HTTPException(status_code=401, detail="Invalid credentials")
    

    token = create_access_token({"sub": str(user.id), "username": user.username, "email":user.email}) #type: ignore
    print("Generated Access Token:", token)  # Debugging line
    refresh_token = create_refresh_token({"sub": str(user.id), "username": user.username, "email":user.email})
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



class ForgotPassword(BaseModel):
    email: str

EXPIRY_TIME = 30

@router.post("/forgot_password")
async def forgot_password(
    data: ForgotPassword,
    background_tasks: BackgroundTasks,
    db: AsyncSession=Depends(get_db)
):
    try:
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar()
        print("UUUUUUUUUUUUUUUUUUUUUUUU",user.email) #type:ignore
        if user is None:
           raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                  detail="Invalid Email address")
        
        secret_token = create_reset_token(email=user.email) #type:ignore
        url = f"http://localhost:8000/auth/forgot_password/{secret_token}"
        
        body = f"""
        <p>Hello,</p>
        <p>You requested a password reset. This link will expire in {EXPIRY_TIME} minutes:</p>
        <a href="{url}">Reset Password</a>
        <br />
        <p>If you didn’t request this, you can ignore this email.</p>
        """

        messages = MessageSchema(
            subject="Password Reset Instructions",
            recipients=[data.email],
            body=body,  
            subtype=MessageType.html
        )

        background_tasks.add_task(fm.send_message, messages)
        
        return JSONResponse(status_code=status.HTTP_200_OK,
            content={"message": "Email has been sent", "success": True,
                "status_code": status.HTTP_200_OK})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="Something Unexpected, Server Error")
        

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str



@router.post("/reset_password")
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = verify_reset_token(data.token)
        print("PPPPPPPPPPPPPPPPPPPP", payload)
        email = payload
        print("ëeeeeeeeeeeeeeeee",email)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(data.new_password)#type:ignore
    await db.commit()

    return {"message": "Password reset successful"}
