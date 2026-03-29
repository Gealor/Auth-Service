from repositories.business_elem_repository import BusinessElementsRepository
from schemas.role_schemas import ListBusinessElementsRead


class BusinessElementService:
    def __init__(self, db_session):
        self.db_session = db_session
        self.business_elem_repo = BusinessElementsRepository(db_session=self.db_session)


    async def get_all_elements(self) -> ListBusinessElementsRead:
        result = await self.business_elem_repo.get_all_elements()
        return result