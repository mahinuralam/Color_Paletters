from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


# Database models
class Palette(Base):
    __tablename__ = "palettes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    dominant_colors = Column(String)
    accent_colors = Column(String)
    is_public = Column(Integer, default=1)  # 1 for public, 0 for private
    users = relationship("UserFavoritePalette", back_populates="palette")

    
class UserDB(Base):
    __tablename__ = "UserDB"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    favorite_palettes = relationship("UserFavoritePalette", back_populates="user")


class UserFavoritePalette(Base):
    __tablename__ = "user_favorite_palettes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("UserDB.id"), index=True)
    palette_id = Column(Integer, ForeignKey("palettes.id"), index=True)

    user = relationship("UserDB", back_populates="favorite_palettes")
    palette = relationship("Palette", back_populates="users")


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

    