from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

import tasks
from app.user import schemas, services, models, permission
from config import settings
from config.settings import MEDIA_PATH
from db.db import get_db

router = APIRouter()


@router.get("/",
            response_model=List[schemas.UserInResponse],
            dependencies=[Depends(permission.get_current_superuser)])
def read_users(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    Retrieve users.
    """
    users = services.user_crud.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/",
             response_model=schemas.UserInResponse,
             dependencies=[Depends(permission.get_current_superuser)])
def create_user(*, db: Session = Depends(get_db), user_in: schemas.UserCreate) -> Any:
    """
    Create new user.
    """
    user = services.user_crud.get(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = services.user_crud.create(db, schema=user_in)
    if settings.EMAILS_ENABLED and user_in.email:
        tasks.celery_send_new_account_email.delay(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        # background_tasks.add_task(
        #     send_new_account_email, email_to=user_in.email, username=user_in.email,
        #     password=user_in.password
        # )
    return user


@router.put("/me", response_model=schemas.UserInResponse)
def update_user_me(
        *,
        db: Session = Depends(get_db),
        password: str = Body(None),
        full_name: str = Body(None),
        email: EmailStr = Body(None),
        current_user: models.User = Depends(permission.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = services.user_crud.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.UserInResponse)
def read_user_me(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(permission.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=schemas.UserInResponse)
def create_user_open(
        *,
        db: Session = Depends(get_db),
        password: str = Body(...),
        email: EmailStr = Body(...),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = services.user_crud.get(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_in = schemas.UserCreate(password=password, email=email)
    user = services.user_crud.create(db, schema=user_in)
    return user


@router.get("/{user_id}", response_model=schemas.UserInResponse)
def read_user_by_id(
        user_id: int,
        current_user: models.User = Depends(permission.get_current_active_user),
        db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = services.user_crud.get(db, id=user_id)
    if user == current_user:
        return user
    if not services.user_crud.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{user_id}",
            response_model=schemas.UserInResponse,
            dependencies=[Depends(permission.get_current_superuser)])
def update_user(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        user_in: schemas.UserUpdate,
) -> Any:
    """
    Update a user.
    """
    user = services.user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = services.user_crud.update(db, db_obj=user, obj_in=user_in)
    return user


@router.post("/follow/{id}")
def follow_user(
        *,
        id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(permission.get_current_active_user)
):
    services.follow(action="follow", db=db, user_id=id, current_user_id=current_user.id)
    return {"msg": "You are not following this user now"}


@router.post("/unfollow/{id}")
def unfollow_user(
        *,
        id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(permission.get_current_active_user)
):
    services.follow(action="unfollow", db=db, user_id=id, current_user_id=current_user.id)
    return {"msg": "Now you follow this user"}


@router.put("/update-avatar/me")
async def update_image_me(
        *,
        db: Session = Depends(get_db),
        image: UploadFile = File(...),
        current_user: models.User = Depends(permission.get_current_active_user)
):
    """
    User updates his own image
    """
    if image.content_type not in ['image/jpeg', 'image/png']:
        raise HTTPException(status_code=406, detail="Only .jpeg or .png  files allowed")

    file_name = services.generate_unique_img_name(image)
    file_path = MEDIA_PATH + file_name
    services.save_image_in_db(db=db, user_id=current_user.id, file_path=file_path)
    services.save_image_in_folder(image=image, file_path=file_path)

    return {
        "id": current_user.id,
        "filename": image.filename
    }


@router.put("/update-avatar/{id}", dependencies=[Depends(permission.get_current_user)])
async def update_image_user(
        *,
        id: int,
        db: Session = Depends(get_db),
        image: UploadFile = File(...),
):
    """
    Superuser updates another user's image
    """
    if image.content_type not in ['image/jpeg', 'image/png']:
        raise HTTPException(status_code=406, detail="Only .jpeg or .png  files allowed")

    file_name = services.generate_unique_img_name(image=image)
    file_path = MEDIA_PATH + file_name
    services.save_image_in_db(db=db, user_id=id, file_path=file_path)
    services.save_image_in_folder(image=image, file_path=file_path)
    return {
        "id": id,
        "filename": file_name
    }
