from pydantic import EmailStr

from core.auth.creation_tokens import create_access_token, create_refresh_token
from core.auth.passwords import compare_hashed_passwords
from core.logger import log
from repositories.role_repository import RoleRepository
from repositories.user_repository import UserRepository
from schemas.exceptions.roles import RoleNotFoundException
from schemas.exceptions.security import PasswordsNotMatchException, UserEmailAlreadyExistsException, UserNotActiveException
from schemas.exceptions.users import UserNotFoundException
from schemas.response_schemas import ResponseSchema
from schemas.user_schemas import TokensResponse, UserRegister, UserRegisterWithRepeatPassword


class AuthService:
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def register_user(
        self,
        user_data: UserRegisterWithRepeatPassword,
    ) -> ResponseSchema:
        if user_data.password != user_data.repeat_password:
            log.error(
                "Password and repeat password do not match: %s != %s",
                user_data.password,
                user_data.repeat_password
            )
            raise PasswordsNotMatchException
        
        user_repo = UserRepository(db_session=self.db_session)

        existing_user = await user_repo.get_user_by_email(user_data.email)
        if existing_user:
            log.error("User with these email already exist")
            raise UserEmailAlreadyExistsException

        role_repo = RoleRepository(db_session=self.db_session)
        
        role = await role_repo.get_role_by_name("user")
        if not role:
            log.error("Role by name '%s' not found", "user")
            raise RoleNotFoundException
        
        user_register_data = UserRegister(**user_data.model_dump())
        await user_repo.create_user(
            user_register_data,
            base_role_id = role.id,
        )

        return ResponseSchema(msg = "Succesful registration. Now you can log in.")
    

    async def login_user(self, email: EmailStr, password: str) -> TokensResponse:
        user_repo = UserRepository(db_session=self.db_session)

        user = await user_repo.get_user_by_email(email=email)
        if not user:
            log.error("User by email %s not found", email)
            raise UserNotFoundException
        
        is_valid = compare_hashed_passwords(
            entered_password=password.encode("utf-8"),
            hashed_password=user.password.encode("utf-8"),
        )
        if not is_valid:
            log.error("Passwords do not match")
            raise PasswordsNotMatchException
        
        if not user.is_active:
            log.error("User with email %s is not active", email)
            raise UserNotActiveException
        
        user_info = await user_repo.get_user_with_role(user_id=user.id)

        access_token = create_access_token(user_info)
        log.info("Access token created.")
        # TODO: сохранять refresh токен в таблицу базы данных, при /refresh пересоздавать access и refresh токены, 
        # а refresh_token перезаписывать в бд для соответствующего id аккаунта
        refresh_token = create_refresh_token(user_info)
        log.info("Refresh token created.")

        log.info("Succesful log in in account: %s", email)
        return TokensResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )