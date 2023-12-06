from app.servicies.database import db
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncSession:
    async with db.session_factory() as session:
        yield session
