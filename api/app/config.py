import os
from dataclasses import dataclass

# class Config:
#     DB_CONFIG = os.getenv(
#         "DB_CONFIG",
#         "postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}".format(
#             DB_USER=os.getenv("POSTGRES_USER"),
#             DB_PASSWORD=os.getenv("POSTGRES_PASSWORD"),
#             DB_HOST=os.getenv("POSTGRES_HOST"),
#             DB_NAME=os.getenv("POSTGRES_DB"),
#         ),
#     )

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