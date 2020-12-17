from datetime import datetime

from pydantic import BaseModel, EmailStr


class ContactBase(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class ContactCreate(ContactBase):
    category_id: int


class ContactUpdate(ContactBase):
    category_id: int


class ContactInResponse(ContactBase):
    id: int
    date: datetime
