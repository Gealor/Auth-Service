from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.mixins.id_pk_mixin import IdPrimaryKeyMixin


class Role(Base, IdPrimaryKeyMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    rules: Mapped[list["AccessRoleRule"]] = relationship(back_populates="role", cascade="all, delete-orphan")


class BusinessElement(Base, IdPrimaryKeyMixin):
    __tablename__ = 'business_elements'
    
    name: Mapped[str] = mapped_column(nullable=False, unique=True)


class AccessRoleRule(Base, IdPrimaryKeyMixin):
    __tablename__ = 'access_roles_rules'
    
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'))
    element_id: Mapped[int] = mapped_column(ForeignKey('business_elements.id', ondelete='CASCADE'))
    
    # Чтение
    read_permission: Mapped[bool] = mapped_column(default=False, server_default="true")
    read_all_permission: Mapped[bool] = mapped_column(default=False, server_default="true")
    
    # Создание
    create_permission: Mapped[bool] = mapped_column(default=False, server_default="false")
    
    # Обновление
    update_permission: Mapped[bool] = mapped_column(default=False, server_default="false")
    update_all_permission: Mapped[bool] = mapped_column(default=False, server_default="false")
    
    # Удаление
    delete_permission: Mapped[bool] = mapped_column(default=False, server_default="false")
    delete_all_permission: Mapped[bool] = mapped_column(default=False, server_default="false")

    role: Mapped["Role"] = relationship(back_populates="rules")
    element: Mapped["BusinessElement"] = relationship()

    __table_args__ = (
        UniqueConstraint("role_id", "element_id", name = "uq_role_element"),
    )