from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.role import AccessRoleRule
from schemas.exceptions.database import DatabaseException
from schemas.role_schemas import AccessRoleRuleCreate, AccessRoleRuleRead, AccessRoleRuleSchemaBase, AccessRoleRuleUpdate
from core.logger import log

class AccessRulesRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    
    async def get_rules_by_id(self, rule_id: int) -> AccessRoleRuleRead | None:
        stmt = (
            select(AccessRoleRule)
            .options(joinedload(AccessRoleRule.element))
            .where(AccessRoleRule.id == rule_id)
        )

        rule = await self.db_session.scalar(stmt)
        if rule is None:
            return None

        return AccessRoleRuleRead.model_validate(rule)
    

    async def get_rules_by_role_id(self, role_id: int) -> list[AccessRoleRuleRead] | None:
        stmt = (
            select(AccessRoleRule)
            .options(joinedload(AccessRoleRule.element))
            .where(AccessRoleRule.role_id == role_id)
        )

        result = await self.db_session.scalars(stmt)
        if result is None:
            return None

        return [AccessRoleRuleRead.model_validate(rule) for rule in result]


    async def create_rule(self, rule_data: AccessRoleRuleCreate):
        dict_data = rule_data.model_dump()
        rule = AccessRoleRule(
            **dict_data
        )

        self.db_session.add(rule)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to create new rule: %s", e)
            raise DatabaseException
        
        await self.db_session.refresh(rule)
        log.info("Create new rule for role_id: %s", rule_data.role_id)


    async def update_rule(
        self,
        rule_id: int,
        update_data: AccessRoleRuleUpdate
    ) -> AccessRoleRuleSchemaBase | None:
        dict_data = update_data.model_dump(exclude_none=True)
        if not dict_data:
            log.warning("There are no new parameters to update")

        stmt = (
            update(AccessRoleRule).values(**dict_data)
            .where(AccessRoleRule.id == rule_id)
            .returning(AccessRoleRule)
        )

        rule = await self.db_session.scalar(stmt)
        if rule is None:
            return None

        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to update rule: %s", e)
            raise DatabaseException
        
        await self.db_session.refresh(rule)
        log.info("Update rule with id=%d", rule_id)
        return AccessRoleRuleSchemaBase.model_validate(rule)
    

    async def delete_rule(self, rule_id: int):
        stmt = delete(AccessRoleRule).where(AccessRoleRule.id == rule_id)
        await self.db_session.execute(stmt)

        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to delete rule: %s", e)
            raise DatabaseException
        
        log.info("Deleted rule with id=%d", rule_id)