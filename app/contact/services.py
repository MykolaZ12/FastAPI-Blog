from app.base.crud import CRUDBase
from pydantic import EmailStr
from sqlalchemy.orm import Session

from . import schemas, models


class CRUDContact(CRUDBase[models.Contact, schemas.ContactCreate, schemas.ContactUpdate]):
    def create_contact_by_email(
            self, db: Session, *, email: EmailStr, category_id: int) -> models.Contact:
        """Add email contact in database"""
        db_obj = self.model(email=email, category_id=category_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


contact_crud = CRUDContact(models.Contact)
