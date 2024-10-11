from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from core import settings
from api import router as api_router
from services.elasticsearch import check_index as es_check_idx


@asynccontextmanager
async def lifespan(app: FastAPI):
    await es_check_idx(index_name=settings.es.articles_index)
    yield


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
