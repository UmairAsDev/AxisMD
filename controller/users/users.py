import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from utils.utils import get_current_user
from typing import List, Optional
from pydantic import BaseModel
from schema.models import User, UserDetail
from database.database import get_db
from sqlalchemy.future import select

router = APIRouter(prefix="/auth", tags=["user"], dependencies=[Depends(get_current_user)])

class UserProfile(BaseModel):
    speciality: str
    subspeciality:str
    objective: str
    output_style:str
    profile_logo: UploadFile
    
    

@router.post("/user_profile")
async def user_profile(
    speciality: str ,
    subspeciality: str,
    objective: str ,
    output_style: str,
    profile_logo: Optional[UploadFile],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ):
    print(f"Current user ID: {current_user.id}")
    try:
        # Save file
        file_path = None
        if profile_logo:
            file_path = f"uploads/{profile_logo.filename}"
            with open(file_path, "wb+") as f:
                f.write(profile_logo.file.read())

        # Check existing profile
        result = await db.execute(select(UserDetail).where(UserDetail.user_id == current_user.id))
        existing_profile = result.scalars().one_or_none()
        if existing_profile:
            raise HTTPException(status_code=400, detail="Profile already exists.")

        # Create new profile
        new_profile = UserDetail(
            user_id=current_user.id,
            specialty=speciality,
            subspecialty=subspeciality,
            objectives=objective,
            output_style=output_style,
            profile_logo=file_path
        )
        db.add(new_profile)
        await db.commit()
        await db.refresh(new_profile)

        return {
            "message": "Profile created successfully",
            "profile": {
                "speciality": new_profile.specialty,
                "subspeciality": new_profile.subspecialty,
                "objective": new_profile.objectives,
                "output_style": new_profile.output_style,
                "profile_logo": new_profile.profile_logo
            }
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
