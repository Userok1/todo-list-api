from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from config import cfg

engine = create_async_engine(
    cfg.POSTGRESQL_URL,
)


async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


def get_db():
    return async_session


class Base(AsyncAttrs, DeclarativeBase):
    pass