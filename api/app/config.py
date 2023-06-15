import os
from dataclasses import dataclass

@dataclass
class Config:
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    DATABASE_URL: str = os.getenv(
        "DB_CONFIG",
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}",
    )

config = Config