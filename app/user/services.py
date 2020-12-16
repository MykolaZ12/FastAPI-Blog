import logging
import re
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Union

import emails
from emails.template import JinjaTemplate
from fastapi import UploadFile, File
from sqlalchemy.orm import Session


from app.base.crud import CRUDBase
from app.user.models import User
from app.user.schemas import UserCreate, UserUpdate
from config import settings
from config.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    def create(self, db: Session, *, schema: UserCreate) -> User:
        db_obj = User(
            email=schema.email,
            hashed_password=get_password_hash(schema.password),
            is_superuser=schema.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user_crud = CRUDUser(User)


def follow(action: str, db: Session, user_id: int, current_user_id: int):
    follower_user = user_crud.get(db=db, id=current_user_id)
    followed_user = user_crud.get(db=db, id=user_id)

    if action == "follow":
        follower_user.following.append(followed_user)
    elif action == "unfollow":
        follower_user.following.remove(followed_user)

    db.add(follower_user)
    db.commit()
    db.refresh(follower_user)
    return follower_user


def send_email(
        email_to: str,
        subject_template: str = "",
        html_template: str = "",
        environment: Dict[str, Any] = {},
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
        template_str = f.read()
    server_host = settings.SERVER_HOST
    link = f"{server_host}/reset-password?token={token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def send_new_account_email(email_to: str, username: str, password: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html") as f:
        template_str = f.read()
    link = settings.SERVER_HOST
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )


def generate_unique_img_name(image: UploadFile = File(...)):
    name, ext = re.split("\.", image.filename)
    file_name = name + f'_{uuid.uuid4().hex}.{ext}'
    return file_name


def save_image_in_db(db: Session, file_path: str, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    user.image = file_path
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def save_image_in_folder(file_path: str, image: UploadFile = File(...)):
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
