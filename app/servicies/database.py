import typing as tp
from asyncio import current_task
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)

from .settings import Settings


class Database:
    def __init__(self, settings: Settings, echo: bool = False) -> None:
        self.engine: AsyncEngine = create_async_engine(
            settings.build_postgres_dsn(),
            echo=echo,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    def get_scoped_session(self) -> async_scoped_session[AsyncSession]:
        return async_scoped_session(self.session_factory, scopefunc=current_task)

    async def get_session(
        self,
    ) -> tp.AsyncGenerator[async_scoped_session[AsyncSession], tp.Any]:
        session: async_scoped_session[AsyncSession] = self.get_scoped_session()
        yield session
        await session.close()


db: tp.Final[Database] = Database(Settings())  # type: ignore
