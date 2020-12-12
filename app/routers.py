from fastapi import APIRouter

from app.user.endpoints import user

router = APIRouter()

router.include_router(user.router, prefix="/user", tags=["user"])