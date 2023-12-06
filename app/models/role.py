import typing as tp
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if tp.TYPE_CHECKING:
    from .user import User


class Role(Base):
    """Справочная информация о ролях в приложении
    id = 1 name = admin
    id = 2 name = investor
    id = 3 name = developer
    """

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(sa.Text)

    users: Mapped[tp.List["User"]] = relationship("User", back_populates="role")


# class UserRole(Base):
#     user_id: Mapped[int] = mapped_column(sa.ForeignKey(User.id), primary_key=True)
#     user: Mapped[User] = relationship(User)
#
#     role_id: Mapped[int] = mapped_column(sa.ForeignKey(Role.id), primary_key=True)
#     role: Mapped[Role] = relationship(Role)
