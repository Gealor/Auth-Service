from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
ENV_TEMPLATE = BASE_DIR / ".env.template"

class RuntimeSettings(BaseModel):
    host: str = '0.0.0.0'
    port: int = 8000

# Чтобы не указывать в .env параметры с начальным идентификатором, например, database как указано в Settings классе
# явно наследуемся от BaseSettings, а не BaseModel и прописываем model_config
class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ENV_TEMPLATE, ENV_FILE),
        case_sensitive=False,
        extra="ignore" # Игнорировать другие переменные в .env
    )

    db_name: Annotated[str, Field(alias="POSTGRES_DB")]
    db_user: Annotated[str, Field(alias="POSTGRES_USER")]
    db_password: Annotated[str, Field(alias="POSTGRES_PASSWORD")]
    db_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    db_port: int = Field(default=6000, alias="POSTGRES_PORT")
    db_echo: bool = False

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ENV_TEMPLATE, ENV_FILE),
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )

    runtime: RuntimeSettings = RuntimeSettings()
    database: DatabaseSettings = Field(default_factory=DatabaseSettings) # при создании класса Settings, 
    # доходя до поля database будет вызываться конструктор DatabaseSettings (не путать с такой инициализацией = DatabaseSettings(), так поле будет хранить объект, вычесленный не динамически, а при определении класса Settings, не создании экземпляра)
    # и DatabaseSettings сам будет искать свои переменные ничего не зная о родительском классе Settings, который тоже ищет параметры в .env файлах

settings = Settings()