from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, EmailStr, Field

if TYPE_CHECKING:
    from schemas.role_schemas import RoleWithRules


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str = Field(examples=["Иван"])
    last_name: str = Field(examples=["Фамилия"])
    patronymic: str = Field(examples=["Иванов"])


class UserRead(BaseModel):
    id: int


class UserRegister(UserBase):
    email: EmailStr = Field(examples=["example@test.com"])
    password: str = Field(examples=["ivan_craft7869"])


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
    role: "RoleWithRules"


class LoginCredentials(BaseModel):
    email: EmailStr = Field(examples=["example@test.com"])
    password: str = Field(examples=["ivan_craft7869"])