from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:wzas1212@localhost:5000/hw11"
    SECRET_KEY_JWT: str = "secret"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: str = "postgres"
    MAIL_PASSWORD: str = "wzzzzz"
    MAIL_FROM: str = "postgres@localhost"
    MAIL_PORT: int = 5432
    MAIL_SERVER: str = "localhost"
    CLD_NAME: str = "abc"
    CLD_API_KEY: int = 326488457974591
    CLD_API_SECRET: str = "secret"

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v):
        if v not in ["HS256", "HS512"]:
            raise ValueError("Algorithm not supported")
        return v

    model_config = ConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()