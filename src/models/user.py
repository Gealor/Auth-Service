from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.mixins.banned_at_mixin import BannedAtMixin
from models.mixins.deleted_at_mixin import DeletedAtMixin
from models.mixins.id_pk_mixin import IdPrimaryKeyMixin
if TYPE_CHECKING:
    from models.role import Role


class User(Base, IdPrimaryKeyMixin, BannedAtMixin, DeletedAtMixin):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    patronymic: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False) # тут хранится хэш пароля

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), unique=False)

    role: Mapped["Role"] = relationship()
