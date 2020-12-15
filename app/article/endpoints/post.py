from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.article import services, schemas
from app.user import permission
from app.user.models import User
from db.db import get_db

router = APIRouter()


class FilterQueryParams:
    def __init__(self,
                 search: Optional[str] = None,
                 skip: int = 0,
                 limit: int = 100,
                 tag: Optional[List[str]] = Query(None),
                 ):
        self.search = search
        self.skip = skip
        self.limit = limit
        self.tag = tag


@router.get("/{slug}", response_model=schemas.PostInResponse)
def get_post(*, slug: str, db: Session = Depends(get_db)):
    post = services.post_crud.get(db=db, slug=slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/", response_model=List[schemas.PostInResponse])
def get_list_posts(db: Session = Depends(get_db), common: FilterQueryParams = Depends()):
    posts = services.post_filters(db=db, skip=common.skip, limit=common.limit, search=common.search,
                                  tag=common.tag)
    if not posts:
        raise HTTPException(status_code=404, detail="Posts not found")
    return posts


@router.post("/", response_model=schemas.PostInResponse)
def create_post(
        *,
        db: Session = Depends(get_db),
        schema: schemas.PostCreate,
        current_user: User = Depends(permission.get_current_active_user),
) -> Any:
    slug = services.generate_slug(schema.title)
    post_in_db = schemas.PostInDB(**schema.dict(), user_id=current_user.id, slug=slug)
    post = services.post_crud.create_with_tags(db=db, post_schema=post_in_db)
    return post


@router.put("/{id}", response_model=schemas.PostUpdate)
def update_post(
        *,
        db: Session = Depends(get_db),
        id: int,
        schema: schemas.PostUpdate,
        current_user: User = Depends(permission.get_current_active_user),
):
    post = services.post_crud.get(db=db, id=id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not current_user.is_superuser and (post.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    post = services.post_crud.update(db=db, db_obj=post, schema=schema)
    return post


@router.delete("/{id}", response_model=schemas.PostBase)
async def delete_post(
        *,
        db: Session = Depends(get_db),
        id: int,
        current_user: User = Depends(permission.get_current_active_user),
):
    post = services.post_crud.get(db=db, id=id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not current_user.is_superuser and (post.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Not enough permissions")
    post = services.post_crud.remove(db=db, id=id)
    return post
