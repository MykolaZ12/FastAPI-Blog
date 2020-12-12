from sqlalchemy.orm import Session


from app.user import schemas, services
from config import settings


def init_db(db: Session) -> None:

    user = services.user_crud.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = services.user_crud.create(db, obj_in=user_in)  # noqa
