from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class UserModel(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str]
    
    todos: Mapped[list[TodoModel]] = relationship(cascade="all, delete")
    

class TodoModel(Base):
    __tablename__ = "todos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    title: Mapped[str]
    description: Mapped[str]
    

class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int | None] = mapped_column(Integer, primary_key=True)
    sub: Mapped[str | None]
    refresh_token: Mapped[str | None]