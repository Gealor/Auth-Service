from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from schemas.role_schemas import RoleWithRules


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str = Field(examples=["Иван"])
    last_name: str = Field(examples=["Фамилия"])
    patronymic: str = Field(examples=["Иванов"])


class UserRead(UserBase):
    id: int


class UserRegister(UserRead):
    email: EmailStr = Field(examples=["example@test.com"])
    password: str = Field(examples=["ivan_craft7869"])
    is_active: bool


class UserRegisterWithRepeatPassword(UserRegister):
    repeat_password: str = Field(examples=["ivan_craft7869"])


class UserUpdate(UserRegister):
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None


class UserDelete(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    is_active: bool = False
    deleted_at: datetime = Field(default_factory=lambda: datetime.now(tz = UTC).replace(tzinfo=None))


class UserChangePassword(BaseModel):
    password: str = Field(examples=["ivan_craft7869"])

class UserInfoForAdmin(UserRegister):
    is_active: bool = Field(examples=[True, False])

    id: int
    role: RoleWithRules


# Auth
class LoginCredentials(BaseModel):
    email: EmailStr = Field(examples=["example@test.com"])
    password: str = Field(examples=["ivan_craft7869"])


class TokensResponse(BaseModel):
    access_token: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30"])
    refresh_token: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30"])
    token_type: str = "bearer"