from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.database import init_db
from api.routers import tenders


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="AI Tender Pipeline", version="1.0.0", lifespan=lifespan)

app.include_router(tenders.router)


@app.get("/health/")
async def health_check():
    return {"status": "healthy"}
