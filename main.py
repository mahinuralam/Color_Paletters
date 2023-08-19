from datetime import datetime, timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT
from database import Base, engine
from models import Palette, PaletteCreate, PaletteResponse, User, UserDB

Base.metadata.create_all(engine)

app = FastAPI()

# Configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        

@app.get('/')
def root():
    return "Welcome"


# Example endpoint: User registration
@app.post("/register", tags=["User"])
def register(user: User, db: Session = Depends(get_session)):
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = pwd_context.hash(user.password)  # Hash the password
    db_user = UserDB(username=user.username, email=user.email, hashed_password=hashed_password)
    signJWT(user.email)
    db.add(db_user)
    db.commit()
    return {"message": "User registered successfully"}


# Example endpoint: User login
@app.post("/login", tags=["User"])
def login(username: str, password: str, db: Session = Depends(get_session)):
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
        accent_colors=palette.accent_colors,
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



@app.post("/palettes/{palette_id}/favorite", dependencies=[Depends(JWTBearer())], response_model=PaletteResponse, tags=["Palettes"])
def favorite_palette(palette_id: int):
    db = SessionLocal()
    palette = db.query(Palette).filter(Palette.id == palette_id).first()
    if not palette:
        db.close()
        raise HTTPException(status_code=404, detail="Palette not found")

    return JSONResponse(content={"message": "Palette added to favorites"})
    
