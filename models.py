from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String

from database import Base


# Database models
class Palette(Base):
    __tablename__ = "palettes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    dominant_colors = Column(String)
    accent_colors = Column(String)
    is_public = Column(Integer, default=1)  # 1 for public, 0 for private
    
    
class UserDB(Base):
    __tablename__ = "UserDB"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    palette_ids =  Column(String)


# API models
class PaletteCreate(BaseModel):
    name: str
    dominant_colors: str
    accent_colors: str
    is_public: Optional[int] = 1


class PaletteResponse(BaseModel):
    id: int
    name: str
    dominant_colors: str
    accent_colors: str
    is_public: int


class User(BaseModel):
    username: str
    email: str
    password: str
    palette_ids:  str

    