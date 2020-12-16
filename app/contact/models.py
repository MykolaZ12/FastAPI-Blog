from sqlalchemy import Column, Integer, String, DateTime, func

from db.db import Base


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    email = Column(String(255), unique=True)
    date = Column(DateTime(timezone=True), server_default=func.now())