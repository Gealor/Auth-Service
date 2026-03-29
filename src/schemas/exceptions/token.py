from schemas.exceptions.base import AppBaseException


class RefreshTokenBaseException(AppBaseException):
    pass


class RefreshTokenNotFoundException(RefreshTokenBaseException):
    pass


class TokenMismatchException(RefreshTokenBaseException):
    pass


class TokensNotMatchException(RefreshTokenBaseException):
    pass