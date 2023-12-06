from pydantic import BaseModel, Field, ConfigDict


class User(BaseModel):
    email: str = Field(..., examples=["test@test.com"])


class UserLogin(BaseModel):
    email: str = Field(..., examples=["test@]test.com"])
    password: str = Field(..., examples=["Test123456"])


class UserCreate(BaseModel):
    first_name: str = Field(..., examples=["Ivan"])
    last_name: str = Field(..., examples=["Ivanov"])
    email: str = Field(..., examples=["test@]test.com"])
    password: str = Field(..., examples=["Test123456"])
    role_id: int = Field(..., examples=[2])


class UserDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    first_name: str = Field(..., examples=["Ivan"])
    last_name: str = Field(..., examples=["Ivanov"])
    email: str = Field(..., examples=["test@]test.com"])
    role: str = Field(..., examples=["investor"])
    algorithms: list[dict]