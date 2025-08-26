from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

metadata = MetaData(schema="AxisMD")
Base = declarative_base(metadata=metadata)
class User(Base):
    __tablename__ = "users"

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


class UserDetail(Base):
    __tablename__ = "user_details"

    
    detail_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialty = Column(String(100), nullable=False)
    subspecialty = Column(String(100), nullable=True)
    objectives = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    audio_path = Column(String(500), nullable=True)
    transcript = Column(Text, nullable=True)
    modified_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    user = relationship("User", back_populates="user_detail")
    


    
    
