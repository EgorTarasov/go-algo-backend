import typing as tp
import sqlalchemy as sa
import sqlalchemy.orm as orm
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, HTTPException

from app.models import User
from app.models.ml_algorithm import Algorithm
from app.schemas.user import UserDto
from app.dependencies import get_session, get_current_user, UserTokenData


router: tp.Final[APIRouter] = APIRouter(prefix="/user")


@router.get("/me")
async def get_user(
    user: UserTokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    stmt = (
        sa.select(User)
        .options(orm.selectinload(User.algorithms).selectinload(Algorithm.versions))
        .options(orm.selectinload(User.role))
        .where(User.id == user.user_id)
    )
    db_user: User | None = (await db.execute(stmt)).unique().scalar()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserDto.model_validate(db_user)
