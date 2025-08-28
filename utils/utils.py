from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database import get_db
from schema.models import User
from utils.jwt_handler import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    payload = verify_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user


