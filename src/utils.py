from fastapi.security import OAuth2PasswordBearer, HTTPBasic
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from passlib.hash import pbkdf2_sha256
from datetime import datetime, timedelta, timezone
import jwt
from typing import Any
import logging

from .models import UserRegister, RefreshTokenInDB, UserInDB, Todo, TodoAdd
from .orm_models import UserModel, RefreshTokenModel, TodoModel
from config import cfg

logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

security = HTTPBasic()


async def add_user(user: UserRegister, db: async_sessionmaker[AsyncSession]) -> None:
    user_in_db = UserModel(name=user.username, email=user.email, password=user.password)
    async with db() as session:
        async with session.begin():
            session.add(user_in_db)


async def get_user(email: str, db: async_sessionmaker[AsyncSession]) -> UserModel | None:
    async with db() as session:
        async with session.begin():
            select_stmt = select(UserModel).where(UserModel.email == email)
            res = (await session.execute(select_stmt)).scalars().first()
            return res


def create_access_token(data: dict[str, Any], expire_at: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expire_at:
        expire = datetime.now(timezone.utc) + expire_at
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    access_token = jwt.encode(to_encode, cfg.ACCESS_TOKEN_SECRET_KEY, cfg.TOKEN_ALGORITHM)
    return access_token


def create_refresh_token(data: dict[str, Any], expire_at: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expire_at:
        expire = datetime.now(timezone.utc) + expire_at
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=cfg.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    refresh_token = jwt.encode(to_encode, cfg.REFRESH_TOKEN_SECRET_KEY, cfg.TOKEN_ALGORITHM)
    return refresh_token


async def get_refresh_token_from_db(email: str, db: AsyncSession) -> RefreshTokenModel | None:
    async with db.begin():
        select_stmt = select(RefreshTokenModel).where(RefreshTokenModel.sub == email) 
        token = (await db.execute(select_stmt)).scalars().first()
        return token
    

async def add_refresh_token(token: RefreshTokenInDB, db: async_sessionmaker[AsyncSession]) -> None:
    token_in_db = RefreshTokenModel(**token.model_dump())
    async with db() as session:
        async with session.begin():
            session.add(token_in_db)


async def authenticate_user(email: str, password: str, db: async_sessionmaker[AsyncSession]) -> UserInDB | None:
    user_in_db = await get_user(email, db)
    user = UserInDB.model_validate(user_in_db)
    if not user:
        return None
    if not pbkdf2_sha256.verify(password, user.password):
        return None

    return user


async def add_todo(todo: TodoAdd, db: async_sessionmaker[AsyncSession]) -> TodoModel | None:
    todo_model = TodoModel(**todo.model_dump())
    async with db() as session:
        async with session.begin():
            session.add(todo_model)
            await session.flush()
            return todo_model
        return None


async def get_todo(todo_id: int, db: async_sessionmaker[AsyncSession]) -> TodoModel | None:
    async with db() as session:
        async with session.begin():
            select_stmt = select(TodoModel).where(TodoModel.id == todo_id)
            res = (await session.execute(select_stmt)).scalars().first()
            return res
    

async def edit_todo(todo_id: int, new_todo: Todo, db: async_sessionmaker[AsyncSession]) -> TodoModel | None:
    async with db() as session:
        async with session.begin():
            update_stmt = update(TodoModel).where(TodoModel.id == todo_id).values(**new_todo.model_dump()).returning(TodoModel)
            res = (await session.execute(update_stmt)).scalars().first()
            await session.flush()
            return res
        

async def remove_todo(todo_id: int, db: async_sessionmaker[AsyncSession]) -> None:
    async with db() as session:
        async with session.begin():
            delete_stmt = delete(TodoModel).where(TodoModel.id == todo_id)
            await session.execute(delete_stmt)
            

async def get_todos(db: async_sessionmaker[AsyncSession], page: int = 1, limit: int = 12) -> list[TodoModel] | None:
    async with db() as session:
        async with session.begin():
            select_stmt = select(TodoModel).limit(limit).offset((page - 1) * 12)
            todos = (await session.execute(select_stmt)).scalars().all()
            return list(todos)