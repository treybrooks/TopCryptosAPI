import os

class Config:
    DB_CONFIG = os.getenv(
        "DB_CONFIG",
        "postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}".format(
            DB_USER=os.getenv("POSTGRES_USER"),
            DB_PASSWORD=os.getenv("POSTGRES_PASSWORD"),
            DB_HOST=os.getenv("POSTGRES_HOST"),
            DB_NAME=os.getenv("POSTGRES_DB"),
        ),
    )
config = Config