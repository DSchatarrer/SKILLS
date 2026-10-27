"""Pydantic settings; old DATASOURCE_* environment keys remain supported."""
from typing import Annotated, Any, Literal
from pydantic import AnyUrl, BeforeValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


def parse_cors(value: Any) -> list[str] | str:
    if isinstance(value, str) and not value.startswith("["):
        return [x.strip() for x in value.split(",") if x.strip()]
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", env_ignore_empty=True
    )

    FASTAPI_SECRET_KEY: str
    FASTAPI_DEBUG: bool = False
    FASTAPI_RUN_HOST: str = "0.0.0.0"
    FASTAPI_RUN_PORT: int = 8080
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    TOKEN_SECONDS_EXP: int = 3600
    API_KEY: str

    # New direct URL override, e.g. sqlite+aiosqlite:///./local.db
    DATABASE_URL: str | None = None
    # Backward-compatible components used in the original .env
    DATASOURCE_DB: str | None = None
    DATASOURCE_PORT: int | None = None
    DATASOURCE_FQDN: str | None = None
    DATASOURCE_USR: str | None = None
    DATASOURCE_PWD: str | None = None
    DATASOURCE_SCHEMA_SYNC: str | None = None
    DATASOURCE_SCHEMA_ASYNC: str | None = None

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = Field(default_factory=list)

    @property
    def SQLALCHEMY_DATABASE_URI_ASYNC(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        required = {
            "DATASOURCE_DB": self.DATASOURCE_DB,
            "DATASOURCE_FQDN": self.DATASOURCE_FQDN,
            "DATASOURCE_SCHEMA_ASYNC": self.DATASOURCE_SCHEMA_ASYNC,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError("Configura DATABASE_URL o: " + ", ".join(missing))
        return URL.create(
            drivername=self.DATASOURCE_SCHEMA_ASYNC,
            username=self.DATASOURCE_USR,
            password=self.DATASOURCE_PWD,
            host=self.DATASOURCE_FQDN,
            port=self.DATASOURCE_PORT,
            database=self.DATASOURCE_DB,
        ).render_as_string(hide_password=False)

    @property
    def server_host(self) -> str:
        fqdn = self.DATASOURCE_FQDN or "localhost"
        return f"{'http' if self.ENVIRONMENT == 'local' else 'https'}://{fqdn}"


settings = Settings()
