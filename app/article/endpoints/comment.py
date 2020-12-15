from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.article import schemas, services, models
from app.user import permission
from app.user.models import User
from db.db import get_db

router = APIRouter()


@router.get("/{id}", response_model=schemas.CommentInResponse)
def get_comment(*, db: Session = Depends(get_db), id: int):
    comment = services.comment_crud.get_without_parent(db=db, id=id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.get("/", response_model=List[schemas.CommentInResponse])
def get_list_comments(*, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comments = services.comment_crud.get_multi_without_parent(skip=skip, limit=limit, db=db)
    if not comments:
        raise HTTPException(status_code=404, detail="Comments not found")
    return comments


@router.post("/{post_id}", response_model=schemas.CommentCreate)
def create_comment(
        *,
        post_id: int,
        schema: schemas.CommentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(permission.get_current_active_user),
):
    comment_in_db = schemas.CommentInDB(**schema.dict(), post_id=post_id, user_id=current_user.id)
    comment = services.comment_crud.create(db=db, schema=comment_in_db)
    return comment


@router.post("/{post_id}/{comment_id}", response_model=schemas.CommentInResponse)
def create_comment_reply(
        *,
        post_id: int,
        comment_id: int,
        schema: schemas.CommentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(permission.get_current_active_user),
):
    extend_comment_in = models.Comment(**schema.dict(), post_id=post_id, parent_id=comment_id,
                                       user_id=current_user.id)
    comment = services.comment_crud.create(db=db, schema=extend_comment_in)
    return comment


@router.put("/{id}", response_model=schemas.CommentUpdate)
def update_comment(
        *,
        id: int,
        schema: schemas.CommentUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(permission.get_current_active_user),
):
    comment = services.comment_crud.get(db=db, id=id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not current_user.is_superuser and (comment.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    comment = services.comment_crud.update(db=db, db_obj=comment, schema=schema)
    return comment


@router.delete("/{id}", response_model=schemas.CommentInResponse)
def delete_comment(
        *,
        id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(permission.get_current_active_user),
):
    comment = services.comment_crud.get(db=db, id=id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not current_user.is_superuser and (comment.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    comment = services.comment_crud.remove(db=db, id=id)
    return comment
