from fastapi import Cookie, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.servicies.database import Database

def get_db():
    with SessionLocal() as db:
        yield db
