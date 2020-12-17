from fastapi import APIRouter

from app.user.endpoints import user, login
from app.article.endpoints import post, comment, tag, like, category
from app.contact.endpoints import contact
router = APIRouter()

router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(login.router, prefix="/user", tags=["login"])
router.include_router(category.router, prefix="/category", tags=["category"])
router.include_router(post.router, prefix="/post", tags=["post"])
router.include_router(like.router, prefix="/post/like", tags=["like"])
router.include_router(comment.router, prefix="/comment", tags=["comment"])
router.include_router(tag.router, prefix="/tag", tags=["tag"])
router.include_router(contact.router, prefix="/post", tags=["contact"])
