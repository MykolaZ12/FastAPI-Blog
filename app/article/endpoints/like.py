from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.article import schemas, models, services
from app.user import permission
from db.db import get_db

router = APIRouter()


@router.post("/{post_id}/", response_model=schemas.Like)
def like_post(
        post_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(permission.get_current_active_user),
):
    if services.has_liked_post(db=db, post_id=post_id, user_id=current_user.id):
        raise HTTPException(status_code=400, detail="Post already liked")
    like = services.like(db=db, post_id=post_id, user_id=current_user.id)
    return like


@router.delete("/{post_id}/", response_model=schemas.Like)
def unlike_post(
        post_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(permission.get_current_active_user),
):
    if not services.has_liked_post(db=db, post_id=post_id, user_id=current_user.id):
        raise HTTPException(status_code=400, detail="Post was not liked")
    unlike = services.unlike(db=db, post_id=post_id, user_id=current_user.id)
    return unlike


@router.get("/{post_id}/")
def count_likes_post(post_id: int, db: Session = Depends(get_db)):
    count_likes = services.count_likes(db=db, post_id=post_id)
    return {"count_likes": count_likes}
