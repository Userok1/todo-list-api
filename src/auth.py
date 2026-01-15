from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from passlib.hash import pbkdf2_sha256
from typing import Annotated, Any
import jwt
from datetime import timedelta

from .models import AccessToken, RefreshToken, RefreshTokenInDB, UserInDB, Tokens, UserRegister
from .orm_models import UserModel
from .utils import (
    authenticate_user, 
    create_access_token, 
    create_refresh_token, 
    add_refresh_token,
    get_user,
    add_user,
    get_refresh_token_from_db,
)
from .database import get_db
from config import cfg

router = APIRouter()


@router.post("/register", response_model=dict)
async def register(
    user_data: UserRegister,
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> Any:
    user_in_db: UserModel | None = await get_user(user_data.email, db)
    if user_in_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User have already registered"
        )
    hashed_password = pbkdf2_sha256.hash(user_data.password)
    user_data.password = hashed_password
    await add_user(user_data, db)
    
    access_token = create_access_token({'sub': user_data.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Tokens)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> Any:
    user: UserInDB | None = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({'sub': user.email})
    refresh_token = create_refresh_token({'sub': user.email})

    refresh_token_data = RefreshTokenInDB(sub=user.email, refresh_token=refresh_token)
    await add_refresh_token(refresh_token_data, db)

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
    

@router.post("/refresh", response_model=AccessToken)
async def refresh_token(
    token: Annotated[RefreshToken, Form()], 
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    try:
        payload = jwt.decode(token.refresh_token, cfg.REFRESH_TOKEN_SECRET_KEY, algorithms=[cfg.TOKEN_ALGORITHM])
        user_email = payload.get('sub')
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        refresh_token_in_db = get_refresh_token_from_db(user_email, db)
        if not refresh_token_in_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token revoked",
            )
        new_access_token = create_access_token(
            {'sub': user_email},
            timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return {"access_token": new_access_token, "token_type": "bearer"}

    except jwt.exceptions.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )