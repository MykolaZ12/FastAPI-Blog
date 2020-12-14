
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.article import schemas, services
from app.auth import permission
from db.db import get_db

router = APIRouter()


@router.get("/{tag_id}", response_model=schemas.TagInResponse)
def get_tag(*, tag_id: int, db: Session = Depends(get_db)):
    tag = services.tag_crud.get(db=db, id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.get("/", response_model=List[schemas.TagInResponse])
def get_list_tag(*, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tag = services.tag_crud.get_multi(skip=skip, limit=limit, db=db)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post("/", response_model=schemas.TagCreate,
             dependencies=[Depends(permission.get_current_superuser)])
def create_tag(
        *,
        db: Session = Depends(get_db),
        schema: schemas.TagCreate,
):
    tag = services.tag_crud.create(db=db, schema=schema)
    return tag


@router.put("/{id}", response_model=schemas.TagUpdate,
            dependencies=[Depends(permission.get_current_superuser)])
def update_tag(
        *,
        db: Session = Depends(get_db),
        id: int,
        schema: schemas.TagUpdate,
):
    tag = services.tag_crud.get(db=db, id=id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    tag = services.tag_crud.update(db=db, db_obj=tag, schema=schema)
    return tag


@router.delete("/{id}", response_model=schemas.TagInResponse,
               dependencies=[Depends(permission.get_current_superuser)])
async def delete_tag(
        *,
        db: Session = Depends(get_db),
        id: int,
):
    tag = services.tag_crud.get(db=db, id=id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    tag = services.tag_crud.remove(db=db, id=id)
    return tag
