from fastapi import FastAPI
import uvicorn

from core import settings

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
