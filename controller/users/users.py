from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])



@router.get("/")
async def user_profile():