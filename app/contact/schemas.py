from datetime import datetime

from pydantic import BaseModel, EmailStr


class ContactBase(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactInResponse(ContactBase):
    id: int
    date: datetime
