from fastapi import APIRouter, Depends, HTTPException, status

from core.auth.security import PermissionChecker, get_current_user
from core.database import db_session_getter
from schemas.response_schemas import ResponseSchema
from schemas.user_schemas import UserInfoForAdmin


router = APIRouter(prefix="/user", tags=["JWT"])

@router.delete("/delete/me")
async def delete_my_account(
    current_user: UserInfoForAdmin = Depends(get_current_user),
    rule = Depends(PermissionChecker("users", "delete")),
    db = Depends(db_session_getter),
) -> ResponseSchema: 
    return ResponseSchema(msg = "Success delete")