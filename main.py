from datetime import datetime, timedelta
from typing import List

import jwt
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from auth.auth_bearer import JWTBearer
from auth.auth_handler import JWT_ALGORITHM, JWT_SECRET, decodeJWT, signJWT
from database import Base, engine
from models import (Palette, PaletteCreate, PaletteResponse, User, UserDB,
                    UserFavoritePalette)

Base.metadata.create_all(engine)

app = FastAPI()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/login")


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        

@app.get('/')
def root():
    return "Welcome"


@app.post("/register", tags=["User"])
def register(user: User, db: Session = Depends(get_session)):
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = pwd_context.hash(user.password)
    db_user = UserDB(username=user.username, email=user.email, hashed_password=hashed_password)
    signJWT(user.email)
    db.add(db_user)
    db.commit()
    
    return {"message": "User registered successfully"}


@app.post("/login", tags=["User"])
async def login(username: str, password: str, db: Session = Depends(get_session)):
    db_user = db.query(UserDB).filter(UserDB.username == username).first()
    if db_user is None or not pwd_context.verify(password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return signJWT(db_user.email)


@app.post("/palettes", dependencies=[Depends(JWTBearer())], response_model=PaletteResponse, tags=["Palettes"])
def create_palette(palette: PaletteCreate):
    db = SessionLocal()
    db_palette = Palette(
        name=palette.name,
        dominant_colors=palette.dominant_colors,
        accent_colors1=palette.accent_colors1,
        accent_colors2=palette.accent_colors2,
        is_public=palette.is_public,
    )
    db.add(db_palette)
    db.commit()
    db.refresh(db_palette)
    db.close()
    palette_response = PaletteResponse(**db_palette.__dict__)
    return palette_response


@app.get("/palettes", response_model=List[PaletteResponse], tags=["Palettes"])
def get_public_palettes():
    db = SessionLocal()
    palettes = db.query(Palette).filter(Palette.is_public == 1).all()
    db.close()
    
    palette_responses = []
    for palette in palettes:
        palette_response = PaletteResponse(**palette.__dict__)
        palette_responses.append(palette_response)
    
    return palette_responses


@app.get("/palettes/search", response_model=List[PaletteResponse], tags=["Palettes"])
def search_palettes(
    search_query: str = Query(None, title="Search query"),
    color_query: str = Query(None, title="Color query"),
):
    db = SessionLocal()
    
    query = db.query(Palette)
    
    if search_query:
        # Search by name
        query = query.filter(Palette.name.ilike(f"%{search_query}%"))
        
    if color_query:
        # Search by color (either dominant_colors or accent_colors)
        query = query.filter(
            or_(
                Palette.dominant_colors.ilike(f"%{color_query}%"),
                Palette.accent_colors1.ilike(f"%{color_query}%"),
                Palette.accent_colors2.ilike(f"%{color_query}%"),
            )
        )
    
    palettes = query.filter(Palette.is_public == 1).all()
    db.close()
    
    palette_responses = []
    for palette in palettes:
        palette_response = PaletteResponse(**palette.__dict__)
        palette_responses.append(palette_response)
    
    return palette_responses


#Get current user information from Token
def get_current_user(token: str = Depends(reuseable_oauth)) -> User:
    try:
        payload = decodeJWT(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return payload.get("user_id")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/palettes/{palette_id}/favorite", dependencies=[Depends(JWTBearer())], response_model=PaletteResponse, tags=["Palettes"])
def favorite_palette(palette_id: int, db: Session = Depends(get_session), current_user: str = Depends(get_current_user)):
    palette = db.query(Palette).filter(Palette.id == palette_id).first()
    if not palette:
        raise HTTPException(status_code=404, detail="Palette not found")
    
    user_db = db.query(UserDB).filter(UserDB.email == current_user).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    favorite_palette = db.query(UserFavoritePalette).filter(
        UserFavoritePalette.user_id == user_db.id,
        UserFavoritePalette.palette_id == palette.id
    ).first()
    
    if favorite_palette:
        raise HTTPException(status_code=400, detail="Palette already saved as favorite")
    
    db_favorite_palette = UserFavoritePalette(user_id=user_db.id, palette_id=palette.id)
    db.add(db_favorite_palette)
    db.commit()
    
    return PaletteResponse(**palette.__dict__)