from fastapi import Depends, HTTPException, status, APIRouter, Header
from fastapi_mail import MessageSchema, ConnectionConfig, FastMail
from starlette.background import BackgroundTasks
from fastapi import Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schema.forms import LoginForm, SignupForm
from pydantic import SecretStr, BaseModel, Field,  EmailStr
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
    MAIL_USERNAME="umairashrafbsse@gmail.com",
    MAIL_PASSWORD=SecretStr("qmjm qiiq pxnf mrlu"), 
    MAIL_FROM="umairashrafbsse@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
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

    result = await db.execute(select(User).where(User.phone_number == form.phone_number))
    existing_user_phone = result.scalar_one_or_none()
    if existing_user_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
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
async def login(
    form_data: LoginForm,
    db: AsyncSession = Depends(get_db),
    response: Response = None,  # type: ignore
):
    result = await db.execute(select(User).where(User.email == form_data.email))
    user = result.scalar_one_or_none()


    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    print("User fetched from DB:", user.__dict__)  

    if not verify_password(form_data.password, user.hashed_password):  # type: ignore
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "username": user.username, "email": user.email})  # type: ignore
    refresh_token = create_refresh_token({"sub": str(user.id), "username": user.username, "email": user.email})

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








class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8, description="New password (min 8 chars)")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password (min 8 chars)")
    


@router.post("/forgot_password")
async def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    token = create_reset_token(user.email)#type:ignore
    reset_link = f"http://localhost:5000/auth/reset_password?token={token}"  

    html = f"""
    <html>
        <body>
            <h3>Password Reset Request</h3>
            <p>Click below to reset your password. This link expires in 30 minutes.</p>
            <a href="{reset_link}">Reset Password</a>
            <br><br>
            <p>If you didn’t request this, ignore this email.</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="Password Reset Instructions",
        recipients=[data.email],
        body=html,
        subtype=MessageType.html,
    )

    background_tasks.add_task(fm.send_message, message)

    return {"message": "Password reset email sent successfully."}



from fastapi import Query



# @router.get("/reset_password")
# async def verify_reset_token_link(token: str = Query(...)):
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         print("pppppppppppppppppppppppppp", payload)
#         return {"message": "Valid token", "email": payload.get("email")}
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid or expired token")






@router.post("/reset_password")
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Query(None),
    authorization: str | None = Header(None),
):
    print(token)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    elif not token:
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    try:
        email = verify_reset_token(token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user.hashed_password = hash_password(data.new_password)#type:ignore
    await db.commit()

    return {"message": "Password reset successful."}
