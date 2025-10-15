from fastapi import APIRouter, Request


router = APIRouter(prefix="/patient", tags=["patients"])

@router.post("/add_patient")
async def add_patients():
    pass