from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from api import router as api_router
from core import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.elasticsearch import check_index as es_check_idx
from services.elasticsearch import es
from services.redis.redis_helper import r_cache


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await es.es_connect()
    await es_check_idx(index_name=settings.es.articles_index)
    yield
    await es.es_close_connection()
    await r_cache.close_pool()


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "https://blogapp.spacejamhd.com",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


def main() -> None:
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
        # workers=4,
        # loop="none",  # for Redis testing
    )


if __name__ == "__main__":
    main()
