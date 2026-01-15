from fastapi import Depends, HTTPException, status
from typing import Annotated
import jwt
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .utils import get_user, oauth2_scheme
from .models import UserInDB
from .database import get_db
from config import cfg


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> UserInDB:
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, cfg.ACCESS_TOKEN_SECRET_KEY, algorithms=[cfg.TOKEN_ALGORITHM])
        user = payload.get('sub')
        if not user:
            raise invalid_credentials
    except jwt.exceptions.PyJWTError:
        raise invalid_credentials
    
    user_in_db = await get_user(user, db)
    user = UserInDB.model_validate(user_in_db)

    if not user:
        raise invalid_credentials

    return user