from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config import config
from app.services.database import sessionmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()

def init_app(init_db: bool =True):
    # useful for testing
    # can create application without initializing the database connection
    # need custome db init for testing
    lifespan = None

    if init_db:
        sessionmanager.init(config.DATABASE_URL)

    server = FastAPI(title="TopCrypto server", lifespan=lifespan)

    from app.main import router as main_router
    from app.views.tokeninfo import router as token_router

    server.include_router(main_router)
    server.include_router(token_router)

    return server