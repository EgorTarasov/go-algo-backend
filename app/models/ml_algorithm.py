import typing as tp
import uuid

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.schemas.features import MlFeatures
from app.schemas.algorithm import BacktestResultsRaw
from .base import Base, TimestampMixin
from .user import User


class Algorithm(Base, TimestampMixin):
    """Основная информация об алгоритме
    - Название (которе указал пользователь)
    - sec_id (название актива, с которым работает алгоритм)

    versions: list[AlgorithmVersion] - версии алгоритма (в отдельной таблице)
    'backtests': list[BacktestResults] - результаты бектеста для алгоритма
    """

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    uuid: Mapped[str] = mapped_column(sa.UUID(as_uuid=True), unique=True, index=True)
    name: Mapped[str] = mapped_column(sa.String(255), default="ml")
    algo_type: Mapped[tp.Literal["ml", "algo"]] = mapped_column(sa.String(4))
    sec_id: Mapped[str] = mapped_column(sa.String(10))

    versions: Mapped[list["AlgorithmVersion"]] = relationship(
        "AlgorithmVersion",
        # backref="algorithm",
    )
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_algorithms",
        backref="algorithm",
        uselist=True,
        # lazy="selectin",
    )

    # @property
    # def uuid(self) -> uuid.UUID:
    #     # TODO: move UUID into .env settings
    #     return encode_uuid3(str(self.id))

    def __repr__(self):
        return f"<Algorithm(id={self.id}, uuid={self.uuid} name={self.name}, sec_id={self.sec_id})>"


class UserAlgorithm(Base):
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    algorithm_id: Mapped[int] = mapped_column(
        sa.ForeignKey("algorithms.id", ondelete="CASCADE"), primary_key=True
    )
    # user: Mapped["User"] = relationship("User")
    # algorithm: Mapped[Algorithm] = relationship(Algorithm)


class AlgorithmVersion(Base, TimestampMixin):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    uuid: Mapped[str] = mapped_column(sa.UUID(as_uuid=True), unique=True, index=True)
    features: Mapped[dict[str, tp.Any] | list[dict[str, tp.Any]]] = mapped_column(
        pg.JSON, nullable=False
    )
    management: Mapped[dict[str, tp.Any]] = mapped_column(pg.JSON, nullable=True)
    nodes: Mapped[list[dict[str, tp.Any]] | dict[str, tp.Any]] = mapped_column(
        pg.JSON, nullable=True
    )
    algorithm_id: Mapped[int] = mapped_column(
        sa.ForeignKey(Algorithm.id, ondelete="CASCADE")
    )
    # algorithm: Mapped[Algorithm] = relationship(Algorithm.id, backref="versions")
    backtests: Mapped[list["AlgorithmBacktest"]] = relationship(
        "AlgorithmBacktest", backref="version"
    )


class AlgorithmBacktest(Base, TimestampMixin):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    version_id: Mapped[int] = mapped_column(
        sa.ForeignKey(AlgorithmVersion.id, ondelete="CASCADE")
    )
    data: Mapped[dict[str, tp.Any]] = mapped_column(pg.JSON)
    graph_url: Mapped[str] = mapped_column(sa.Text)

    def __repr__(self) -> str:
        return f"<AlgorithmBacktest(id={self.id}, version_id={self.version_id})>"
