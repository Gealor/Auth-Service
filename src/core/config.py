import logging
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
CERTS_PATH = BASE_DIR / "core" / "auth" / "certs"
ENV_FILE = BASE_DIR / ".env"
ENV_TEMPLATE = BASE_DIR / ".env.template"

class RuntimeSettings(BaseModel):
    host: str = '0.0.0.0'
    port: int = 8000
    reload: bool = True

class LoggerSettings(BaseModel):
    LOG_DEFAULT_FORMAT: str = (
        "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
    )
    level: int = logging.INFO
    datefmt: str = "%Y-%m-%d %H:%M:%S"

class AuthSettings(BaseModel):
    private_key: Path = CERTS_PATH / "jwt-private.pem" # для подписывания токенов (создания)
    public_key: Path = CERTS_PATH / "jwt-public.pem" # для декодирования токенов
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    @property
    def refresh_token_expire_minutes(self):
        return 24 * 60 * self.refresh_token_expire_days

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
    auth: AuthSettings = AuthSettings()
    log: LoggerSettings = LoggerSettings()

settings = Settings()