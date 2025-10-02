from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from api import router as api_router
from core import settings
from fastapi import FastAPI
from services.elasticsearch import check_index as es_check_idx, es


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await es.es_connect()
    await es_check_idx(index_name=settings.es.articles_index)
    yield
    es.es_close_connection()


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
        # workers=4,
        # loop="none",  # for Redis testing
    )
