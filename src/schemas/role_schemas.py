from pydantic import BaseModel, ConfigDict, Field

# BusinessElement schemas
class BusinessElementSchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(examples=["role", "user", "rule"])


class BusinessElementSchemaWithID(BusinessElementSchemaBase):
    id: int = Field(examples=[1, 2, 3])


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
    rules: list[AccessRoleRuleSchemaBase]