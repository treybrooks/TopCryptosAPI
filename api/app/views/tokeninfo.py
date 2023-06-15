from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database import get_db

from ..models import TokenInfo as TokenInfoModel


router = APIRouter(prefix="/token", tags=["token"])

class TokenSchemaBase(BaseModel):
    symbol: str | None = None
    rank: int | None = None
    price: float | None = None
    created_at: datetime | None = None

class TokenSchemaCreate(TokenSchemaBase):
    pass

class TokenSchema(TokenSchemaBase):
    id: str

    class Config:
        orm_mode = True

@router.get("/get-token", response_model=TokenSchema)
async def get_token(id: str, db: AsyncSession = Depends(get_db)):
    token = await TokenInfoModel.get(db, id)
    return token

@router.get("/get-tokens", response_model=list[TokenSchema])
async def get_tokens(db: AsyncSession = Depends(get_db)):
    tokens = await TokenInfoModel.get_all(db)
    return tokens

@router.get("/get-tokens-by-date", response_model=list[TokenSchema])
async def get_tokens_by_date(dt: datetime, db: AsyncSession = Depends(get_db)):
    tokens = await TokenInfoModel.get_tokens_by_date(db, dt)
    return tokens

@router.post("/create-token", response_model=TokenSchema)
async def create_token(token: TokenSchemaCreate, db: AsyncSession = Depends(get_db)):
    token = await TokenInfoModel.create(db, **token.dict())
    return token