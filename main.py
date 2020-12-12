import uvicorn
from fastapi import FastAPI
from app.routers import router
from config import settings

app = FastAPI()

app.include_router(router, prefix=settings.API_V1_STR)


