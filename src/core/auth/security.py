from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.creation_tokens import ACCESS_TOKEN_TYPE, decode_jwt
from core.logger import log
from core.database import db_session_getter
from repositories.user_repository import UserRepository
from schemas.user_schemas import UserRead


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(db_session_getter)
) -> UserRead:
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        
        if type_token := payload.get("type") != ACCESS_TOKEN_TYPE:
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

    user = await UserRepository(db_session=db).get_user_by_id(user_id=user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="The user was not found or deleted"
        )
    return user