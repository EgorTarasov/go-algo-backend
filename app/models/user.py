import typing as tp
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .role import Role

if tp.TYPE_CHECKING:
    from .ml_algorithm import Algorithm


class User(Base, TimestampMixin):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    first_name: Mapped[str] = mapped_column(sa.Text)
    last_name: Mapped[str] = mapped_column(sa.Text)
    email: Mapped[str] = mapped_column(sa.Text)
    password: Mapped[str] = mapped_column(sa.Text)
    role_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey(Role.id))

    role: Mapped["Role"] = relationship("Role")

    algorithms: Mapped[list["Algorithm"]] = relationship(
        "Algorithm",
        secondary="user_algorithms",
        uselist=True,
        backref="user"
        # secondaryjoin="user_algorithms.user_id == users.id",
    )

    def __repr__(self) -> str:
        return f"<User {self.id} {self.first_name} {self.last_name} {self.email}>"
