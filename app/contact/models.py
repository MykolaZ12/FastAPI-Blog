from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from db.db import Base


class Contact(Base):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    email = Column(String(255), unique=True)
    date = Column(DateTime(timezone=True), server_default=func.now())

    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship("Category", back_populates="contact")
