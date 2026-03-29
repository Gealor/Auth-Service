from fastapi import APIRouter, Depends, HTTPException, status

from core.auth.security import get_current_user, get_current_user_for_refresh
from core.database import db_session_getter
from core.logger import log
from schemas.exceptions.database import DatabaseException
from schemas.exceptions.roles import RoleNotFoundException
from schemas.exceptions.security import PasswordsNotMatchException, UserEmailAlreadyExistsException, UserNotActiveException
from schemas.exceptions.token import RefreshTokenBaseException
from schemas.exceptions.users import UserNotFoundException
from schemas.response_schemas import ResponseSchema
from schemas.user_schemas import LoginCredentials, TokensResponse, UserInfoForAdmin, UserRegisterWithRepeatPassword
from services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["JWT"])


@router.post("/register")
async def create_user(
    user_data: UserRegisterWithRepeatPassword,
    db = Depends(db_session_getter),
) -> ResponseSchema:
    try:
        result = await AuthService(db_session=db).register_user(user_data)
    except PasswordsNotMatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Passwords do not match"
        )
    except UserEmailAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The user with this email already exists"
        )
    except RoleNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="The base role of 'user' was not found in the database"
        )
    except Exception as e:
        log.error("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unexpected error"
        )
    
    return result


@router.post("/login")
async def login_user(
    credentials: LoginCredentials,
    db = Depends(db_session_getter),
) -> TokensResponse:
    try:
        result = await AuthService(db_session=db).login_user(
            email = credentials.email, 
            password = credentials.password,
        )
    except (UserNotFoundException, PasswordsNotMatchException):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )
    except UserNotActiveException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Account deleted or blocked"
        )
    except Exception as e:
        log.error("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unexpected error"
        )
    
    return result


@router.post("/refresh")
async def refresh_access_token(
    user_data: tuple[UserInfoForAdmin, str] = Depends(get_current_user_for_refresh),
    db = Depends(db_session_getter),
) -> TokensResponse:
    user, refresh_token = user_data
    try:
        result = await AuthService(db_session=db).refresh_tokens(
            user=user, 
            raw_refresh_token=refresh_token
        )
    except RefreshTokenBaseException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired refresh token"
        )
    except Exception as e:
        log.error("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unexpected error"
        )
        
    return result


@router.post("/logout")
async def logout(
    current_user: UserInfoForAdmin = Depends(get_current_user),
    db = Depends(db_session_getter),
):
    try:
        await AuthService(db_session=db).logout_user(user_id=current_user.id)
    except Exception as e:
        log.error("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unexpected error during logout"
        )
    
    return {"msg": "Successfully logged out."}