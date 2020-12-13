from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

from db.db import Base

user_to_user = Table(
    'user_to_user', Base.metadata,
    Column("follower_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("followed_id", Integer, ForeignKey("user.id"), primary_key=True)
)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    full_name = Column(String(255))
    date_registrations = Column(DateTime(), default=datetime.utcnow, index=True)
    last_login = Column(DateTime(), nullable=True)
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    avatar = Column(String, nullable=True)

    post = relationship("Post", back_populates="user")

    comment = relationship("Comment", back_populates="user")

    liked = relationship("PostLike",
                         foreign_keys='PostLike.user_id',
                         backref='user', lazy='dynamic'
                         )

    following = relationship("User",
                             secondary="user_to_user",
                             primaryjoin="User.id==user_to_user.c.follower_id",
                             secondaryjoin="User.id==user_to_user.c.followed_id",
                             backref="followers"
                             )