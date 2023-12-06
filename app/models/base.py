from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        name = cls.__name__[0].lower() + cls.__name__[1:]
        name = "".join(c if c.islower() else f"_{c.lower()}" for c in name)
        return f"{name}s"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(
            default=sa.func.now(),
            onupdate=sa.func.now(),
            server_default=sa.func.now(),
    )
