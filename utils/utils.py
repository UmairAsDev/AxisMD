from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database import get_db
from schema.models import User
from jose import jwt, JWTError, ExpiredSignatureError
from tools.settings import settings 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db : AsyncSession = Depends(get_db)):
    try:
        print("Secret:", settings.SECRET_KEY)
        print("Algorithm:", settings.ALGORITHM)
        print(f"Verifying token: {token}")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"Decoded payload: {payload}")
        user_id = payload.get("sub") #type: ignore
        print(f"Extracted user_id: {type(user_id)} - {user_id}")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        try:
            user_id = int(user_id)   # handles str or int both
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid token format")
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

