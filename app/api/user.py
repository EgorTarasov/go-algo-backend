import typing as tp
import sqlalchemy as sa
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, HTTPException

from app.models import User
from app.schemas.user import UserDto
from app.dependencies import get_session, get_current_user, UserTokenData


router: tp.Final[APIRouter] = APIRouter(prefix="/user")


@router.get("/me")
async def get_user(
    user_data: UserTokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    stmt = sa.select(User).where(User.id == user_data.user_id)
    user: User | None = (await db.execute(stmt)).scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserDto.model_validate(user)
