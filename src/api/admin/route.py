from fastapi import APIRouter, Depends, HTTPException, status

from core.auth.security import PermissionChecker, get_current_user
from core.database import db_session_getter
from core.logger import log
from repositories.role_repository import RoleRepository
from schemas.exceptions.roles import RoleNotFoundException, RuleNotFoundException
from schemas.role_schemas import AccessRoleRuleRead, AccessRoleRuleSchemaBase, AccessRoleRuleUpdate, ListRoleWithRules, RoleWithRules
from schemas.user_schemas import UserInfoForAdmin
from services.permission_service import PermissionService


router = APIRouter(prefix="/admin/roles", tags=["Admin"])

@router.get("/")
async def get_all_roles(
    page: int = 1,
    per_page: int = 10,
    current_user: UserInfoForAdmin = Depends(get_current_user),
    rule = Depends(PermissionChecker("permissions", "read")),
    db = Depends(db_session_getter),
) -> ListRoleWithRules:
    role_repo = RoleRepository(db_session=db)
    
    # Вызываем ваш новый метод
    all_roles = await role_repo.get_all_roles_and_his_rules(page = page, per_page = per_page)
    
    return all_roles

@router.get("/{role_id}/rules")
async def get_role_rules(
    role_id: int,
    current_user: UserInfoForAdmin = Depends(get_current_user),
    rule: AccessRoleRuleRead = Depends(PermissionChecker("permissions", "read")),
    db = Depends(db_session_getter),
) -> RoleWithRules:
    try:
        role = await PermissionService(db_session=db).get_role_permissions(role_id)
    except RoleNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Role not found",
        )
    except Exception as e:
        log.error("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unexpected error"
        )
    
    return role


@router.patch("/rules/{rule_id}")
async def update_role_rule(
    rule_id: int,
    update_data: AccessRoleRuleUpdate,
    current_user: UserInfoForAdmin = Depends(get_current_user),
    rule: AccessRoleRuleRead = Depends(PermissionChecker("permissions", "update")),
    db = Depends(db_session_getter),
) -> AccessRoleRuleSchemaBase:
    try:
        updated_rule = await PermissionService(db_session=db).update_access_rule(
            rule_id=rule_id, 
            update_data=update_data
        )
    except RuleNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found",
        )
    except Exception as e:
        log.error("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unexpected error"
        )
    
    return updated_rule
    