from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from models.tokens import RefreshToken
from core.logger import log
from schemas.exceptions.database import DatabaseException
from schemas.exceptions.token import RefreshTokenNotFoundException

class TokenRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


    async def get_token_by_user_id(self, user_id: int) -> str | None:
        stmt = select(RefreshToken.token).where(RefreshToken.user_id == user_id)

        token_hash = await self.db_session.scalar(stmt)
        if token_hash is None:
            return None

        return token_hash
    

    async def create_record(self, user_id: int, token_hash: str):
        record = RefreshToken(
            user_id = user_id,
            token = token_hash,
        )
        self.db_session.add(record)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to add refresh_token: %s", e)
            raise DatabaseException
        
        await self.db_session.refresh(record)
        log.info("Add refresh token for user with id: %s", record.user_id)


    async def update_record(self, user_id: int, token: str) -> str:
        stmt = (
            update(RefreshToken).values(token = token)
            .where(RefreshToken.user_id == user_id)
            .returning(RefreshToken)
        )

        record = await self.db_session.scalar(stmt)
        if record is None:
            raise RefreshTokenNotFoundException

        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to update refresh_token: %s", e)
            raise DatabaseException
        
        await self.db_session.refresh(record)
        log.info("Update refresh token for user_id=%d", record.user_id)
        return record.token
    

    async def delete_token(self, user_id: int):
        stmt = delete(RefreshToken).where(RefreshToken.user_id == user_id)
        await self.db_session.execute(stmt)

        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to delete refresh token: %s", e)
            raise DatabaseException
        
        log.info("Deleted refresh token with user_id=%d", user_id)
