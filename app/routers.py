from fastapi import APIRouter

from app.user.endpoints import user, login
from app.article.endpoints import post, comment, tag

router = APIRouter()

router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(login.router, prefix="/user", tags=["login"])
router.include_router(post.router, prefix="/post", tags=["post"])
router.include_router(comment.router, prefix="/comment", tags=["comment"])
router.include_router(tag.router, prefix="/tag", tags=["tag"])