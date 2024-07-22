from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, LargeBinary

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    confirmed = Column(Boolean, default=False)

class Models(Base):
    __tablename__ = "ml_models"
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String)
    model = Column(LargeBinary)