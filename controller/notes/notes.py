import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from sqlalchemy.future import select
from app.graph import build_voice_agent_graph


router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("generate_notes")
async def generate_notes(request:Request, db:AsyncSession=Depends(get_db)):
    pass



@router.put("/edit_notes")
async def edit_notes():
    pass