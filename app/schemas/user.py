import typing as tp
from pydantic import BaseModel, Field, ConfigDict
from .algorithm import AlgorithmDto

UserRoles = tp.Literal[2, 3]


class UserRole(BaseModel):
    id: int = Field(..., alias="id")
    name: str = Field()

    model_config = ConfigDict(
        from_attributes=True,
    )


class User(BaseModel):
    email: str = Field(..., examples=["test@test.com"])


class UserLogin(BaseModel):
    email: str = Field(..., examples=["test@]test.com"])
    password: str = Field(..., examples=["Test123456"])


class UserCreate(BaseModel):
    first_name: str = Field(..., examples=["Ivan"])
    last_name: str = Field(..., examples=["Ivanov"])
    email: str = Field(..., examples=["test@test.com"])
    password: str = Field(..., examples=["Test123456"])
    role_id: UserRoles = Field(...)


class UserDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    first_name: str = Field(..., examples=["Ivan"])
    last_name: str = Field(..., examples=["Ivanov"])
    email: str = Field(..., examples=["test@]test.com"])
    role: UserRole = Field(..., examples=["investor"])
    algorithms: list[AlgorithmDto]
