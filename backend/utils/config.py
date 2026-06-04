import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "FlareGas Intelligence Platform"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "sqlite:///./data/flaregas.db"
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "flare-gas-prediction"

    model_path: str = "./models"
    data_path: str = "./data"

    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
