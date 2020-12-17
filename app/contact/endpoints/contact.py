from fastapi import APIRouter, Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.contact.models import Contact
from app.contact import services, schemas
from db.db import get_db

router = APIRouter()


@router.post("/subscription/{category_id}/{email}")
def newsletter_subscription(
        email: EmailStr, category_id: int, db: Session = Depends(get_db)) -> Contact:
    contact = services.contact_crud.create_contact_by_email(
        email=email, category_id=category_id, db=db
    )
    return contact
