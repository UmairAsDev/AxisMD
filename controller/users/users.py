import os
import sys
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel
from schema.models import User, UserDetail
from database.database import get_db
from sqlalchemy import select, update, func

router = APIRouter(prefix="/user",tags=["user"])
    

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
        file_path = None
        if profile_logo:
            file_path = f"uploads/{profile_logo.filename}"
            with open(file_path, "wb+") as f:
                f.write(profile_logo.file.read())


        result = await db.execute(select(UserDetail).where(UserDetail.user_id == user_id))
        existing_profile = result.scalars().one_or_none()
        if existing_profile:
            raise HTTPException(status_code=400, detail="Profile already exists.")

        new_profile = UserDetail(
            user_id=user_id,
            speciality=speciality,
            subspeciality=subspeciality,
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
                "speciality": new_profile.speciality,
                "subspeciality": new_profile.subspeciality,
                "objective": new_profile.objectives,
                "output_style": new_profile.output_style,
                "profile_logo": new_profile.profile_logo,
                "created_at": new_profile.created_at
            }
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))



@router.put("/edit_user_profile")
@router.patch("/user_profile")
async def edit_user_profile(
    request: Request,
    speciality:str = Form(None, description="speciality"),
    subspeciality: str = Form(None, description="subspeciality"),
    objective: str = Form(None, description="objectives"),
    output_style: str = Form(None, description="Style"),
    profile_logo: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    ):
    try:
        user_id = int(request.state.user["sub"])
        result = await db.execute(select(UserDetail).where(UserDetail.user_id == user_id))
        existing_profile = result.scalars().one()

        
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found. Please create a profile first.")
        
        file_path = existing_profile.profile_logo
        if profile_logo:
            if existing_profile.profile_logo and os.path.exists(existing_profile.profile_logo):#type:ignore
                os.remove(existing_profile.profile_logo)#type:ignore
            
            file_path = f"uploads/{user_id}_{profile_logo.filename}"
            print(f"profile file path....{file_path}")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb+") as f:
                shutil.copyfileobj(profile_logo.file, f)
        

   
        update_data = {}
        if speciality is not None:
            update_data["speciality"] = speciality
        if subspeciality is not None:
            update_data["subspeciality"] = subspeciality
        if objective is not None:
            update_data["objectives"] = objective
        if output_style is not None:
            update_data["output_style"] = output_style
        if profile_logo is not None:
            update_data["profile_logo"] = file_path
        
        if update_data:
            await db.execute(update(UserDetail).where(UserDetail.user_id == user_id).values(**update_data))
            await db.commit()
            
            result = await db.execute(select(UserDetail).where(UserDetail.user_id == user_id))
            updated_profile = result.scalars().one()
            
            return {
                "message": "Profile updated successfully",
                "profile": {
                    "speciality": updated_profile.speciality,
                    "subspeciality": updated_profile.subspeciality,
                    "objective": updated_profile.objectives,
                    "output_style": updated_profile.output_style,
                    "profile_logo": updated_profile.profile_logo,
                    "updated_at": updated_profile.created_at
                }
            }
        else:
            return {
                "message": "No changes provided",
                "profile": {
                    "speciality": existing_profile.speciality,
                    "subspeciality": existing_profile.subspeciality,
                    "objective": existing_profile.objectives,
                    "output_style": existing_profile.output_style,
                    "profile_logo": existing_profile.profile_logo
                }
            }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    

@router.get("/get_user_profile")
async def get_profile(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_id = int(request.state.user["sub"])
    result = await db.execute(select(UserDetail).where(UserDetail.user_id == user_id))
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "speciality": profile.speciality,
        "subspeciality": profile.subspeciality,
        "objective": profile.objectives,
        "output_style": profile.output_style,
        "profile_logo": profile.profile_logo,
        "created_at": profile.created_at,
        "updated_at": profile.modified_at
    }




@router.delete("/user_profile/logo")
async def delete_profile_logo(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_id = int(request.state.user["sub"])
    result = await db.execute(select(UserDetail).where(UserDetail.user_id == user_id))
    profile = result.scalars().one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if profile.profile_logo and os.path.exists(profile.profile_logo):#type:ignore
        os.remove(profile.profile_logo)#type:ignore
    

    stmt = (
        update(UserDetail)
        .where(UserDetail.user_id == user_id)
        .values(profile_logo=None)
    )
    await db.execute(stmt)
    await db.commit()
    
    return {"message": "Profile logo deleted successfully"}