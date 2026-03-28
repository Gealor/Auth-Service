from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from sqlalchemy.orm import joinedload

from models.role import Role
from models.user import User
from schemas.exceptions.database import DatabaseException
from schemas.user_schemas import UserDelete, UserInfoForAdmin, UserRead, UserRegister, UserUpdate
from core.logger import log

class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    
    async def get_user_by_email(self, email: str) -> UserRegister | None:
        stmt = select(User).where(User.email == email)

        user = await self.db_session.scalar(stmt)
        if user is None:
            return None

        return UserRegister.model_validate(user)
    
    async def get_user_by_id(self, user_id: int) -> UserRead | None:
        stmt = select(User).where(User.id == user_id)

        user = await self.db_session.scalar(stmt)
        if user is None:
            return None
        
        return UserRead.model_validate(user)


    async def get_user_with_role(self, user_id: int) -> UserInfoForAdmin | None:
        stmt = (
            select(User)
            .options(joinedload(User.role).selectinload(Role.rules))
            .where(User.id == user_id)
        )

        user = await self.db_session.scalar(stmt)
        if user is None:
            return None
        
        return UserInfoForAdmin.model_validate(user)
    

    async def create_user(self, user_data: UserRegister, base_role_id: int):
        user = User(
            first_name = user_data.first_name,
            last_name = user_data.last_name,
            patronymic = user_data.patronymic,
            email = user_data.email,
            password = bcrypt.hashpw(
                user_data.password.encode("utf-8"),
                salt = bcrypt.gensalt(),
            ).decode("utf-8"),
            role_id = base_role_id,
            is_active = True,
        )
        
        self.db_session.add(user)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to create user: %e", e)
            raise DatabaseException
        
        await self.db_session.refresh(user)
        log.info("Create new user with id=%d", user.id)

    async def update_user(self, user_id: int, update_data: UserUpdate) -> UserRead:
        dict_data = update_data.model_dump(exclude_none=True)

        stmt = (
            update(User).values(**dict_data)
            .where(User.id==user_id)
            .returning(User)
        )
        user = await self.db_session.scalar(stmt)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to update user: %s", e)
            raise DatabaseException
        
        await self.db_session.refresh(user)
        log.info("Update user with id=%d", user_id)
        return UserRead.model_validate(user)

    async def delete_user(self, user_id: int):
        delete_info = UserDelete()
        dict_data = delete_info.model_dump()

        stmt = (
            update(User).values(**dict_data).where(User.id == user_id)
        )
        await self.db_session.execute(stmt)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to delete user: %s", e)
            raise DatabaseException
        
        log.info("Deleted user with id=%d", user_id)
    