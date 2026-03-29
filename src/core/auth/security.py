from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.creation_tokens import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, decode_jwt
from core.logger import log
from core.database import db_session_getter
from repositories.user_repository import UserRepository
from schemas.role_schemas import AccessRoleRuleRead
from schemas.user_schemas import UserInfoForAdmin


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(db_session_getter)
) -> UserInfoForAdmin:
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        type_token = payload.get("type")
        if type_token != ACCESS_TOKEN_TYPE:
            log.error("An access token was expected, got %s", type_token)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="An access token was expected, and a different type of token was received"
            )
            
        user_id_str: str | None = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
        user_id = int(user_id_str)
        
    except jwt.PyJWTError as e:
        log.error("Error decode token: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired token"
        )

    user = await UserRepository(db_session=db).get_user_with_role(user_id=user_id)

    if not user or not user.is_active:
        log.error("User with id=%d is not active or not exist", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="The user was not found or deleted"
        )
    return user


async def get_current_user_for_refresh(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(db_session_getter)
) -> tuple[UserInfoForAdmin, str]:
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        type_token = payload.get("type")
        
        if type_token != REFRESH_TOKEN_TYPE:
            log.error("A refresh token was expected, got %s", type_token)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="A refresh token was expected, and a different type of token was received"
            )
            
        user_id_str: str | None = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
        user_id = int(user_id_str)
        
    except jwt.PyJWTError as e:
        log.error("Error decode token: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired token"
        )

    user = await UserRepository(db_session=db).get_user_with_role(user_id=user_id)

    if not user or not user.is_active:
        log.error("User with id=%d is not active or not exist", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="The user was not found or deleted"
        )
        
    return user, token


class PermissionChecker:
    def __init__(self, element_name: str, action: str):
        self.element_name = element_name
        self.action = action 


    def _found_target_rule(self, current_user: UserInfoForAdmin) -> AccessRoleRuleRead | None:
        for rule in current_user.role.rules:
            if rule.element.name == self.element_name:
                return rule
            
        return None

    async def __call__(
        self, 
        current_user: UserInfoForAdmin = Depends(get_current_user)
    ) -> AccessRoleRuleRead:
        # Правило для конкретного бизнес-модуля
        target_rule = self._found_target_rule(current_user)

        if not target_rule:
            log.error("Not found '%s' element for role %s", self.element_name, current_user.role)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this module")

        # Проверка флагов (например, update_permission или update_all_permission)
        base_perm = getattr(target_rule, f"{self.action}_permission", False)
        all_perm = getattr(target_rule, f"{self.action}_all_permission", False)

        if not (base_perm or all_perm):
            log.error("Not found '%s' permission for role %s", self.action, current_user.role.name)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action forbidden")

        return target_rule