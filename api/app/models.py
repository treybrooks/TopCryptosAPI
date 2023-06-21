from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, select, delete
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database import Base


class TokenInfo(Base):
    __tablename__ = "TokenInfo"
    created_at = Column(DateTime, primary_key=True)
    symbol = Column(String, primary_key=True)
    rank = Column(Integer, nullable=False)
    price = Column(Float, nullable=True)

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        transaction = cls(**kwargs)
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction
    
    @classmethod
    async def delete_timestamp(cls, db: AsyncSession, created_at: datetime):
        transaction = delete(cls).where(
            cls.created_at==created_at
        ).returning(cls.symbol, cls.created_at)
        await db.execute(transaction)
        await db.commit()
        return transaction
    
    @classmethod
    async def get_tokens_by_date(cls, db: AsyncSession, dt: datetime):
        return (await db.execute(
            select(cls).filter_by(created_at=dt)
        )).scalars().all()
