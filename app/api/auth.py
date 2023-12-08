import typing as tp
import logging
from fastapi.background import P

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm


from app.dependencies.db import get_session
from app.auth import jwt, security
from app.models.role import Role
from app.schemas.user import UserCreate, UserLogin
from app.schemas.token import Token, TokenData

from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
) -> Token:
    """Вход по почте и паролю"""
    try:
        # stmt = sa.select(User).where(User.email == form_data.username)
        # get User with role_data
        stmt = (
            sa.select(User)
            .options(orm.selectinload(User.role))
            .where(User.email == form_data.username)
        )
        db_user: User | None = (await db.execute(stmt)).unique().scalar_one_or_none()

        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        if security.PasswordManager.verify_password(
            form_data.password, db_user.password
        ):
            token = jwt.JWTEncoder.create_access_token(
                db_user.id, db_user.email, db_user.role_id
            )
            return Token.model_validate(
                {
                    "accessToken": token,
                    "role": db_user.role.name,
                }
            )
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


@router.post("/register")
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_session),
):
    """Регистрация нового пользователя"""

    stmt = (
        sa.select(User)
        .options(orm.selectinload(User.role))
        .where(User.email == user.email)
    )
    db_user: User | None = (await db.execute(stmt)).unique().scalar_one_or_none()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    else:
        role_stmt = sa.select(Role).where(Role.id == user.role_id)
        db_role: Role | None = (
            (await db.execute(role_stmt)).unique().scalar_one_or_none()
        )
        if db_role is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role not found",
            )
        db_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password="",
        )
        db_user.role = db_role
        db_user.password = security.PasswordManager.hash_password(user.password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        token = jwt.JWTEncoder.create_access_token(
            db_user.id, db_user.email, db_user.role_id
        )
        return Token.model_validate(
            {
                "accessToken": token,
                "role": db_role.name,
            }
        )
