from schemas.exceptions.base import AppBaseException


class BaseUserException(AppBaseException):
    pass


class UserNotFoundException(BaseUserException):
    pass