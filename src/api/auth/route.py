from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import db_session_getter
from schemas.exceptions.database import DatabaseException
from schemas.exceptions.roles import RoleNotFoundException
from schemas.exceptions.security import PasswordsNotMatchException, UserEmailAlreadyExistsException, UserNotActiveException
from schemas.exceptions.users import UserNotFoundException
from schemas.user_schemas import LoginCredentials, TokensResponse, UserRegisterWithRepeatPassword
from services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["JWT"])


@router.post("/register")
async def create_user(
    user_data: UserRegisterWithRepeatPassword,
    db: AsyncSession = Depends(db_session_getter),
):
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
    except DatabaseException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unexpected error"
        )
    
    return result


@router.post("/login")
async def login_user(
    credentials: LoginCredentials,
    db: AsyncSession = Depends(db_session_getter),
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unexpected error"
        )
    
    return result