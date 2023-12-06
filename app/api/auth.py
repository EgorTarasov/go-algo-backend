import typing as tp
import logging

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm


from app.dependencies.db import get_session
from app.auth import jwt, security
from app.schemas.user import UserCreate, UserLogin
from app.schemas.token import Token, TokenData

from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """Вход по почте и паролю"""
    try:
        stmt = sa.select(User).where(User.email == form_data.username)
        db_user: User | None = (await db.execute(stmt)).scalar_one_or_none()
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        if security.PasswordManager.verify_password(
            form_data.password, db_user.password
        ):
            token = jwt.JWTEncoder.create_access_token(
                db_user.id, db_user.email, db_user.role_id
            )
            return Token(access_token=token, token_type="Bearer")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
    except Exception as e:
        logging.error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )


@router.post("/register", response_model=Token)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_session),
):
    """Регистрация нового пользователя"""
    try:
        stmt = sa.select(User).where(User.email == user.email)
        db_user: User | None = (await db.execute(stmt)).scalar_one_or_none()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        else:
            db_user = User(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                password="",
                role_id=user.role_id,
            )
            db_user.password = security.PasswordManager.hash_password(user.password)
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            token = jwt.JWTEncoder.create_access_token(
                db_user.id, db_user.email, db_user.role_id
            )
            return Token(access_token=token, token_type="Bearer")
    except Exception as e:
        logging.error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
