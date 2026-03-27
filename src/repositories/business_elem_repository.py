from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.role import BusinessElement
from schemas.exceptions.database import DatabaseException
from core.logger import log
from schemas.role_schemas import BusinessElementCreate, BusinessElementRead, BusinessElementUpdate

class BusinessElementsRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    
    async def get_element_by_id(self, elem_id: int) -> BusinessElementRead | None:
        stmt = (
            select(BusinessElement)
            .where(BusinessElement.id == elem_id)
        )

        elem = await self.db_session.scalar(stmt)
        if elem is None:
            return None

        return BusinessElementRead.model_validate(elem)
    

    async def create_elem(self, elem_data: BusinessElementCreate):
        dict_data = elem_data.model_dump()
        elem = BusinessElement(
            **dict_data
        )

        self.db_session.add(elem)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to create new element: %s", e)
            raise DatabaseException
        
        await self.db_session.refresh(elem)
        log.info("Create new elem with elem_id: %s", elem.id)


    async def update_elem(
        self,
        elem_id: int,
        update_data: BusinessElementUpdate
    ) -> BusinessElementRead:
        dict_data = update_data.model_dump(exclude_none=True)
        if not dict_data:
            log.warning("There are no new parameters to update")

        stmt = (
            update(BusinessElement).values(**dict_data)
            .where(BusinessElement.id == elem_id)
            .returning(BusinessElement)
        )

        elem = await self.db_session.scalar(stmt)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to update element: %s", e)
            raise DatabaseException
        
        await self.db_session.refresh(elem)
        log.info("Update element with id=%d", elem_id)
        return BusinessElementRead.model_validate(elem)
    

    async def delete_elem(self, elem_id: int):
        stmt = delete(BusinessElement).where(BusinessElement.id == elem_id)
        await self.db_session.execute(stmt)

        try:
            await self.db_session.commit()
        except IntegrityError as e:
            log.error("Failed to delete elem: %s", e)
            raise DatabaseException
        
        log.info("Deleted element with id=%d", elem_id)