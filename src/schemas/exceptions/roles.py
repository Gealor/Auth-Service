from schemas.exceptions.base import AppBaseException

# Base
class BaseRoleException(AppBaseException):
    pass

class BaseRuleException(AppBaseException):
    pass


# Custom
class RoleNotFoundException(BaseRoleException):
    pass


class RuleNotFoundException(BaseRuleException):
    pass 