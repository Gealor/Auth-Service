from schemas.exceptions.base import AppBaseException


class BaseRoleException(AppBaseException):
    pass


class RoleNotFoundException(BaseRoleException):
    pass