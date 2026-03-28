from core.logger import log
from repositories.role_repository import RoleRepository
from repositories.user_repository import UserRepository
from schemas.exceptions.users import UserNotDeletedException, UserNotFoundException
from schemas.response_schemas import ResponseSchema
from schemas.user_schemas import UserRead, UserUpdate


class UserService:
    def __init__(self, db_session):
        self.db_session = db_session


    async def update_user(
        self,
        user_id: int,
        update_data: UserUpdate,
        exclude_inactive: bool = True
    ) -> UserRead:
        user_repo = UserRepository(db_session=self.db_session)

        user = await user_repo.update_user(
            user_id = user_id,
            update_data = update_data,
            exclude_inactive = exclude_inactive,
        )
        if not user:
            raise UserNotFoundException

        return user

    
    async def delete_self_user(self, user_id: int) -> ResponseSchema:
        user_repo = UserRepository(db_session=self.db_session)
        await user_repo.delete_user(user_id=user_id)
        return ResponseSchema(msg = "Account successfully deleted. You have been logged out.")


    async def restore_deleted_user(self, user_id: int) -> ResponseSchema:
        user_repo = UserRepository(db_session=self.db_session)

        user = await user_repo.get_user_by_id(user_id=user_id)
        if not user:
            raise UserNotFoundException
        
        if not (user.deleted_at or user.is_active):
            raise UserNotDeletedException
        
        await user_repo.restore_user(user_id=user_id)
        return ResponseSchema(msg = "User successfully restored")