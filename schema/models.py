import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Text, MetaData
from sqlalchemy.orm import relationship, declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "AxisMD"}
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(25), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(15), unique=True, nullable=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_login = Column(DateTime(timezone=True), server_default=func.now())
    
    is_active = Column(Boolean, default=True)

    user_detail = relationship("UserDetail", back_populates="user", uselist=False)


class UserDetail(Base):
    __tablename__ = "user_profile"
    __table_args__ = {"schema": "AxisMD"}

    detail_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("AxisMD.users.id"), index=True, nullable=False)
    specialty = Column(String(100), nullable=False)
    subspecialty = Column(String(100), nullable=True)
    profile_logo = Column(String(500), nullable=True)
    objectives = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    output_style = Column(String(100), nullable=False)
    modified_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    user = relationship("User", back_populates="user_detail")
    notes_details = relationship("Notes", back_populates="user_details")


class Notes(Base):
    __tablename__ = "notes"
    __table_args__ = {"schema": "AxisMD"}
    
    notes_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_detail_id = Column(Integer, ForeignKey("AxisMD.user_profile.detail_id"), nullable=False)
    audio_path = Column(String(500), nullable=True)
    transcript = Column(Text, nullable=True)
    content = Column(Text, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    user_details = relationship("UserDetail", back_populates="notes_details")


class Patient(Base):
    __tablename__ = "patient"
    __table_args__ = {"schema": "AxisMD"}
    
    patient_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    physician = Column(Integer, ForeignKey("AxisMD.user_profile.detail_id"), index=True, nullable=False)
    patient_firstname = Column(String(255), index=True, nullable=False)
    patient_lastname = Column(String(255), index=True, nullable=False)
    gender = Column(String(50), index=True, nullable=False)
    age = Column(Integer, index=True, nullable=False)
    diagnosis = Column(Text, index=True, nullable=False)
    icd_code = Column(String(255), index=True, nullable=False)
    procedure_code = Column(String(255), index=True, nullable=False)