from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Integer, Float, DateTime, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database import Base


class TokenInfo(Base):
    __tablename__ = "TokenInfo"
    id = Column(String, primary_key=True)
    symbol = Column(String, nullable=False)
    rank = Column(Integer, nullable=False)
    price = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False)

    @classmethod
    async def create(cls, db: AsyncSession, id=None, **kwargs):
        if not id:
            id = uuid4().hex

        transaction = cls(id=id, **kwargs)
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction

    @classmethod
    async def get(cls, db: AsyncSession, id: str):
        try:
            transaction = await db.get(cls, id)
        except NoResultFound:
            return None
        return transaction

    @classmethod
    async def get_all(cls, db: AsyncSession):
        return (await db.execute(select(cls))).scalars().all()
    
    @classmethod
    async def get_tokens_by_date(cls, db: AsyncSession, dt: datetime):
        return (await db.execute(
            select(cls).filter_by(created_at=dt)
        )).scalars().all()
