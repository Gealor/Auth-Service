from core.logger import log
from repositories.role_repository import RoleRepository
from repositories.user_repository import UserRepository
from schemas.response_schemas import ResponseSchema


class UserService:
    def __init__(self, db_session):
        self.db_session = db_session

    
    async def delete_self_user(self, user_id: int) -> ResponseSchema:
        user_repo = UserRepository(db_session=self.db_session)
        await user_repo.delete_user(user_id=user_id)
        return ResponseSchema(msg = "Account successfully deleted. You have been logged out.")
