from repositories.access_rules_repository import AccessRulesRepository
from repositories.role_repository import RoleRepository
from schemas.exceptions.roles import RoleNotFoundException, RuleNotFoundException
from schemas.response_schemas import ResponseSchema
from schemas.role_schemas import AccessRoleRuleCreate, AccessRoleRuleUpdate


class PermissionService:
    def __init__(self, db_session):
        self.db_session = db_session
        self.role_repo = RoleRepository(db_session)
        self.rule_repo = AccessRulesRepository(db_session)


    async def get_role_permissions(self, role_id: int):
        role = await self.role_repo.get_role_with_access_rules_by_id(role_id)
        if role is None:
            raise RoleNotFoundException

        return role


    async def update_access_rule(self, rule_id: int, update_data: AccessRoleRuleUpdate):
        updated_rule = await self.rule_repo.update_rule(rule_id, update_data)
        if updated_rule is None:
            raise RuleNotFoundException
        return updated_rule
    

    async def add_access_rule(self, rule_data: AccessRoleRuleCreate) -> ResponseSchema:
        await self.rule_repo.create_rule(rule_data)
        return ResponseSchema(msg = "Rule successfully created")


    async def remove_access_rule(self, rule_id: int) -> ResponseSchema:
        existing_rule = await self.rule_repo.get_rules_by_id(rule_id)
        if not existing_rule:
            raise RuleNotFoundException
            
        await self.rule_repo.delete_rule(rule_id)
        return ResponseSchema(msg = f"Rule {rule_id} successfully deleted")