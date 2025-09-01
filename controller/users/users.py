import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Text
from pydantic import BaseModel
from schema.models import User, UserDetail
from schema.forms import UserProfileForm
from database.database import get_db
from sqlalchemy.future import select

router = APIRouter( tags=["user"])



# @router.post("/user_profile")
# async def user_profile(
#     request: Request,
#     form: UserProfileForm,
#     profile_logo: Optional[UploadFile] = File(None),
#     db: AsyncSession = Depends(get_db),
#     ):
#     print(f"Current user ID: {request.state.user['sub']}")
#     try:
#         file_path = None
#         if profile_logo:
#             file_path = f"uploads/{profile_logo.filename}"
#             with open(file_path, "wb+") as f:
#                 f.write(profile_logo.file.read())

    
#         result = await db.execute(select(UserDetail).where(UserDetail.user_id == request.state.user['sub']))
#         existing_profile = result.scalars().first()
#         if existing_profile:
#             raise HTTPException(status_code=400, detail="Profile already exists.")

    
#         new_profile = UserDetail(
#             user_id=request.state.user['sub'],
#             specialty=form.speciality,
#             subspecialty=form.subspeciality,
#             objectives=form.objective,
#             output_style=form.output_style,
#             profile_logo=file_path,
#         )
#         db.add(new_profile)
#         await db.commit()
#         await db.refresh(new_profile)
#         return {
#             "message": "Profile created successfully",
#             "profile": {
#                 "speciality": new_profile.specialty,
#                 "subspeciality": new_profile.subspecialty,
#                 "objective": new_profile.objectives,
#                 "output_style": new_profile.output_style,
#                 "profile_logo": new_profile.profile_logo,
#                 "created_at": new_profile.created_at
#             }
#         }

#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(status_code=400, detail=str(e))

    

@router.post("/user_profile")
async def user_profile(
    request: Request,
    speciality: str = Form(...),
    subspeciality: str = Form(...),
    objective: str = Form(...),
    output_style: str = Form(...),
    profile_logo: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    ):
    try:
        user_id = int(request.state.user["sub"])
        # Save file
        file_path = None
        if profile_logo:
            file_path = f"uploads/{profile_logo.filename}"
            with open(file_path, "wb+") as f:
                f.write(profile_logo.file.read())

        # Check existing profile
        result = await db.execute(select(UserDetail).where(UserDetail.user_id == user_id))
        existing_profile = result.scalars().one_or_none()
        if existing_profile:
            raise HTTPException(status_code=400, detail="Profile already exists.")

        # Create new profile
        new_profile = UserDetail(
            user_id=user_id,
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
                "profile_logo": new_profile.profile_logo,
                "created_at": new_profile.created_at
            }
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
