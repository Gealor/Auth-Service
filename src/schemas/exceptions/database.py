from schemas.exceptions.base import AppBaseException


class BaseDatabaseException(AppBaseException):
    pass


class DatabaseException(BaseDatabaseException):
    pass