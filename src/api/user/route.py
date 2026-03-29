from fastapi import APIRouter, Depends, HTTPException, status

from core.auth.security import PermissionChecker, get_current_user
from core.database import db_session_getter
from core.logger import log
from schemas.exceptions.users import UserNotDeletedException, UserNotFoundException
from schemas.response_schemas import ResponseSchema
from schemas.role_schemas import AccessRoleRuleRead
from schemas.user_schemas import UserInfo, UserInfoForAdmin, UserRead, UserUpdate
from services.user_service import UserService


router = APIRouter(prefix="/user", tags=["JWT"])

@router.get("/me")
async def read_me(
    current_user: UserInfoForAdmin = Depends(get_current_user),
    rule: AccessRoleRuleRead = Depends(PermissionChecker("users", "read")),
) -> UserInfo:
    return UserInfo.model_validate(current_user)

@router.patch("/update/me")
async def update_my_profile(
    update_data: UserUpdate,
    current_user: UserInfoForAdmin = Depends(get_current_user),
    rule: AccessRoleRuleRead = Depends(PermissionChecker("users", "update")),
    db = Depends(db_session_getter),
) -> UserRead:
    try:
        result = await UserService(db_session=db).update_user(
            user_id=current_user.id,
            update_data=update_data
        )
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        log.error("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unexpected error"
        )
    
    return result

@router.delete("/delete/me")
async def delete_my_account(
    current_user: UserInfoForAdmin = Depends(get_current_user),
    rule: AccessRoleRuleRead = Depends(PermissionChecker("users", "delete")),
    db = Depends(db_session_getter),
) -> ResponseSchema:
    try:
        result = await UserService(db_session=db).delete_self_user(user_id=current_user.id)
    except Exception as e:
        log.error("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unexpected error"
        )
    
    return result

@router.patch("/restore")
async def restore_user(
    user_id: int,
    db = Depends(db_session_getter)
) -> ResponseSchema:
    try:
        result = await UserService(db_session=db).restore_deleted_user(user_id=user_id)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    except UserNotDeletedException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User not deleted"
        )
    except Exception as e:
        log.error("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unexpected error"
        )
    
    return result