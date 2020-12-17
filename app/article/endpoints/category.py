from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.article import schemas, services
from app.user import permission
from app.user.models import User
from db.db import get_db

router = APIRouter()


@router.get("/{slug}", response_model=schemas.CategoryInResponse)
def get_category(*, slug: str, db: Session = Depends(get_db)):
    category = services.category_crud.get(db=db, slug=slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/", response_model=List[schemas.CategoryInResponse])
def get_list_categories(*, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> Any:
    categories = services.category_crud.get_multi(skip=skip, limit=limit, db=db)
    if not categories:
        raise HTTPException(status_code=404, detail="Categories not found")
    return categories


@router.post("/", response_model=schemas.CategoryInResponse)
def create_category(
        *,
        db: Session = Depends(get_db),
        schema: schemas.CategoryCreate,
        current_user: User = Depends(permission.get_current_active_user),
) -> Any:
    slug = services.generate_slug(schema.name)
    category_in_db = schemas.CategoryInDB(**schema.dict(), user_id=current_user.id, slug=slug)
    category = services.category_crud.create(db=db, schema=category_in_db)
    return category


@router.put("/{id}", response_model=schemas.CategoryUpdate)
def update_category(
        *,
        db: Session = Depends(get_db),
        id: int,
        schema: schemas.CategoryUpdate,
        current_user: User = Depends(permission.get_current_active_user),
):
    category = services.category_crud.get(db=db, id=id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if not current_user.is_superuser and (category.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    category = services.category_crud.update(db=db, db_obj=category, schema=schema)
    return category


@router.delete("/{id}", response_model=schemas.CategoryInResponse)
async def delete_category(
        *,
        db: Session = Depends(get_db),
        id: int,
        current_user: User = Depends(permission.get_current_active_user),
):
    category = services.category_crud.get(db=db, id=id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if not current_user.is_superuser and (category.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Not enough permissions")
    category = services.category_crud.remove(db=db, id=id)
    return category
