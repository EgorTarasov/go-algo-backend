import typing as tp
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict
from .features import MlFeatures


class RiskManagementParameters(BaseModel):
    balance: float = Field(..., description="Баланс")
    max_balance_for_trading: float = Field(..., description="Максимальный баланс для торговли")
    min_balance_for_trading: float = Field(..., description="Минимальный баланс для торговли")
    part_of_balance_for_buy: float = Field(..., description="Доля баланса для покупки")
    sum_for_buy_rur: float = Field(..., description="Сумма для покупки в рублях")
    sum_for_buy_num: float = Field(..., description="Сумма для покупки в количестве")
    part_of_balance_for_sell: float = Field(..., description="Доля баланса для продажи")
    sum_for_sell_rur: float = Field(..., description="Сумма для продажи в рублях")
    sum_for_sell_num: float = Field(..., description="Сумма для продажи в количестве")
    sell_all: bool = Field(..., description="Продавать все")


class AlgorithmBase(BaseModel):
    sec_id: str = Field(...)
    name: str = Field(...)


class AlgorithmVersionBase(BaseModel):

    features: MlFeatures = Field(...)
    management: RiskManagementParameters = Field(...)


class AlgorithmVersionUpdate(AlgorithmVersionBase):
    ...


class AlgorithmVersionDto(BaseModel):
    id: int
    features: MlFeatures = Field(...)
    management: RiskManagementParameters | None = None
    created_at: tp.Optional[tp.Any] = None
    updated_at: tp.Optional[tp.Any] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class AlgorithmCreate(AlgorithmBase):
    ...


class AlgorithmCreateResponse(AlgorithmBase):
    uuid: UUID


class AlgorithmDto(AlgorithmBase):
    uuid: UUID
    versions: list[AlgorithmVersionDto]

    model_config = ConfigDict(
        from_attributes=True,
    )
