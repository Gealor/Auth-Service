from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.role import AccessRoleRule, Role
from schemas.exceptions.database import DatabaseException
from schemas.role_schemas import RoleCreate, RoleRead, RoleUpdate, RoleWithRules
from core.logger import log

class RoleRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    
    async def get_role_by_name(self, name: str) -> RoleRead | None:
        stmt = select(Role).where(Role.name == name)

        role = await self.db_session.scalar(stmt)
        if role is None:
            return None

        return RoleRead.model_validate(role)
    

    async def get_role_by_id(self, role_id: int) -> RoleRead | None:
        stmt = select(Role).where(Role.id == role_id)

        role = await self.db_session.scalar(stmt)
        if role is None:
            return None

        return RoleRead.model_validate(role)
    

    async def get_role_with_access_rules_by_id(self, role_id: int) -> RoleWithRules | None:
        stmt = (
            select(Role)
            .options(
                selectinload(Role.rules).joinedload(AccessRoleRule.element)
            ).where(Role.id == role_id)
        )

        result = self.db_session.scalar(stmt)
        if result is None:
            return None
        
        return RoleWithRules.model_validate(result)


    async def create_role(self, role_data: RoleCreate):
        role = Role(
            name = role_data.name,
        )

        self.db_session.add(role)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to create new role: %s", e)
            raise DatabaseException
        
        await self.db_session.refresh(role)
        log.info("Create new role with name: %s", role_data.name)


    async def update_role(self, role_id: int, update_data: RoleUpdate) -> RoleRead:
        dict_data = update_data.model_dump(exclude_none=True)
        if not dict_data:
            log.warning("There are no new parameters to update")

        stmt = (
            update(Role).values(**dict_data)
            .where(Role.id == role_id)
            .returning(Role)
        )

        role = await self.db_session.scalar(stmt)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to update role: %s", e)
            raise DatabaseException
        
        await self.db_session.refresh(role)
        log.info("Update role with id=%d, new name=%s", role_id, update_data.name)
        return RoleRead.model_validate(role)
    

    async def delete_role(self, role_id: int):
        stmt = delete(Role).where(Role.id == role_id)
        await self.db_session.execute(stmt)

        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to delete role: %s", e)
            raise DatabaseException
        
        log.info("Deleted role with id=%d", role_id)

