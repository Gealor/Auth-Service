from pydantic import BaseModel, ConfigDict, Field

# BusinessElement schemas
class BusinessElementSchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(examples=["role", "user", "rule"])


class BusinessElementRead(BusinessElementSchemaBase):
    id: int = Field(examples=[1, 2, 3])


class BusinessElementCreate(BusinessElementSchemaBase):
    pass


class BusinessElementUpdate(BusinessElementSchemaBase):
    name: str | None = None


# AccessRoleRule schemas
class AccessRoleRuleSchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_id: int 
    element_id: int
    
    # Чтение
    read_permission: bool = Field(default=True)
    read_all_permission: bool = Field(default=True)
    
    # Создание
    create_permission: bool = Field(default=False)
    
    # Обновление
    update_permission: bool = Field(default=False)
    update_all_permission: bool = Field(default=False)
    
    # Удаление
    delete_permission: bool = Field(default=False)
    delete_all_permission: bool = Field(default=False)


class AccessRoleRuleRead(AccessRoleRuleSchemaBase):
    id: int = Field(examples=[1, 2, 3])
    element: BusinessElementRead


class AccessRoleRuleCreate(AccessRoleRuleSchemaBase):
    pass


class AccessRoleRuleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Чтение
    read_permission: bool | None = None
    read_all_permission: bool | None = None
    
    # Создание
    create_permission: bool | None = None
    
    # Обновление
    update_permission: bool | None = None
    update_all_permission: bool | None = None
    
    # Удаление
    delete_permission: bool | None = None
    delete_all_permission: bool | None = None

# Role schemas
class RoleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(examples=["superadmin", "admin", "user"])


class RoleRead(RoleBase):
    id: int = Field(examples=[1, 2, 3])


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    name: str | None = None


class RoleWithRules(RoleBase):
    rules: list[AccessRoleRuleRead]


class RoleWithRulesAndID(RoleWithRules):
    id: int

class ListRoleWithRules(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    roles: list[RoleWithRulesAndID]