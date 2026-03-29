from pydantic import EmailStr

from core.auth.creation_tokens import create_access_token, create_refresh_token
from core.auth.passwords import compare_hashed_passwords
from core.auth.tokens import compare_hashed_tokens, hash_tokens
from core.logger import log
from repositories.role_repository import RoleRepository
from repositories.token_repository import TokenRepository
from repositories.user_repository import UserRepository
from schemas.exceptions.roles import RoleNotFoundException
from schemas.exceptions.security import PasswordsNotMatchException, UserEmailAlreadyExistsException, UserNotActiveException
from schemas.exceptions.token import TokenMismatchException, TokensNotMatchException
from schemas.exceptions.users import UserNotFoundException
from schemas.response_schemas import ResponseSchema
from schemas.user_schemas import TokensResponse, UserInfoForAdmin, UserRegister, UserRegisterWithRepeatPassword


class AuthService:
    def __init__(self, db_session):
        self.db_session = db_session
        self.user_repo = UserRepository(db_session=self.db_session)
        self.role_repo = RoleRepository(db_session=self.db_session)
        self.token_repo = TokenRepository(db_session=self.db_session)
    

    async def _save_refresh_token(self, user_id: int, refresh_token: str):
        # Хэш токена перед сохранением в БД (как пароль)
        token_hash = hash_tokens(refresh_token).decode("utf-8")
        
        existing_token = await self.token_repo.get_token_by_user_id(user_id)
        if existing_token:
            await self.token_repo.update_record(user_id, token_hash)
        else:
            await self.token_repo.create_record(user_id, token_hash)


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

        existing_user = await self.user_repo.get_user_by_email(user_data.email)
        if existing_user:
            log.error("User with these email already exist")
            raise UserEmailAlreadyExistsException
        
        role = await self.role_repo.get_role_by_name("user")
        if not role:
            log.error("Role by name '%s' not found", "user")
            raise RoleNotFoundException
        
        user_register_data = UserRegister(**user_data.model_dump())
        await self.user_repo.create_user(
            user_register_data,
            base_role_id = role.id,
        )

        return ResponseSchema(msg = "Succesful registration. Now you can log in.")
    

    async def login_user(self, email: EmailStr, password: str) -> TokensResponse:
        user = await self.user_repo.get_user_by_email(email=email)
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
        
        user_info = await self.user_repo.get_user_with_role(user_id=user.id)

        access_token = create_access_token(user_info)
        log.info("Access token created.")
        refresh_token = create_refresh_token(user_info)
        await self._save_refresh_token(
            user_id=user.id,
            refresh_token=refresh_token,
        )
        log.info("Refresh token created and saved.")


        log.info("Succesful log in in account: %s", email)
        return TokensResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    
    
    async def logout_user(self, user_id: int):
        await self.token_repo.delete_token(user_id)
        log.info("User id=%d logged out, refresh token deleted", user_id)


    async def refresh_tokens(
        self, 
        user: UserInfoForAdmin, 
        raw_refresh_token: str
    ) -> TokensResponse:
        db_token_hash = await self.token_repo.get_token_by_user_id(user.id)
        if not db_token_hash:
            log.error("Refresh token not found in DB for user_id=%d", user.id)
            raise TokenMismatchException

        is_valid = compare_hashed_tokens(
            raw_token=raw_refresh_token.encode("utf-8"),
            hashed_token=db_token_hash.encode("utf-8")
        )
        if not is_valid:
            log.error("Refresh tokens do not match")
            raise TokensNotMatchException

        new_access_token = create_access_token(user)
        new_refresh_token = create_refresh_token(user)

        await self._save_refresh_token(user.id, new_refresh_token)

        log.info("Successfully refreshed tokens for user_id=%d", user.id)
        return TokensResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )