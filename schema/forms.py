from pydantic import BaseModel, EmailStr, Field
from fastapi import UploadFile
from typing import Optional, Literal,Text
from datetime import datetime


class LoginForm(BaseModel): 
    email: EmailStr = Field(..., description="Enter your email address")
    password: str = Field(..., min_length=8, max_length=128)


class SignupForm(BaseModel):
    username: str = Field(..., description="Username")
    first_name: str = Field(..., min_length=2, max_length=100, description="First Name")
    last_name: str = Field(..., min_length=2, max_length=100, description="Last Name")
    email: EmailStr = Field(..., description="Email Address")
    phone_number: Optional[str] = Field(None, max_length=15, description="Phone Number")
    password: str = Field(..., min_length=8, max_length=128, description="Password")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Confirm Password")
    

class UserProfileForm(BaseModel):
    speciality: str = Field(..., description="Speciality")
    subspeciality: str = Field(..., description="Subspeciality")
    objective: Text = Field(..., description="Objective")
    output_style :Literal['Comprehensive', 'Focused', 'Categorized'] = Field(..., description="Preferred Output Style")
    

class EditProfile(BaseModel):
    pass