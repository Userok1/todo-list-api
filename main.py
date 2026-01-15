from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from contextlib import asynccontextmanager

from src.auth import router as auth_router
from src.routes import router as todo_router
from src.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Rate limitting
    redis_connection = redis.from_url("redis://localhost", encoding="utf-8", decode_responses=True) 
    await FastAPILimiter.init(redis_connection)
    # Database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()
    
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan, dependencies=[Depends(RateLimiter(times=100, seconds=60))])
app.include_router(router=auth_router)
app.include_router(router=todo_router)


@app.get("/")
def root():
    return {"msg": "Hello world!"}