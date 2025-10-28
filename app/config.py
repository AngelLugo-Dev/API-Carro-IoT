from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = Field(default="IoT Car Control API")
    environment: str = Field(default="production")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=5500)

    # CORS
    cors_allow_origins: list[str] = Field(default_factory=lambda: [
        "*",
        "https://angellugo-dev.github.io",
        "https://angellugo-dev.github.io/frontend-web-iot",
        "https://angellugo-dev.github.io/frontend-web-iot/",
    ])

    # Database (MySQL on AWS RDS)
    db_host: str = Field(default="instance-iot.cjsq62eqm24v.us-east-1.rds.amazonaws.com")
    db_port: int = Field(default=3306)
    db_user: str = Field(default="admin")
    db_password: str = Field(default="")  # set via env: IOT_DB_PASSWORD
    db_name: str = Field(default="iot_car_control")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()  # reads from environment/.env
