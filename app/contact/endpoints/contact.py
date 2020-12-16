from fastapi import APIRouter, Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.contact.models import Contact
from app.contact import services, schemas
from db.db import get_db

router = APIRouter()


@router.post("/subscription/{email}")
def newsletter_subscription(email: EmailStr, db: Session = Depends(get_db)) -> Contact:
    contact = services.contact_crud.create_contact_by_email(email=email, db=db)
    return contact
