from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship, backref

from app.user.models import User
from db.db import Base


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    title = Column(String(255))
    text = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_updated = Column(DateTime(timezone=True), onupdate=func.now())

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User, back_populates="post")

    comment = relationship("Comment", back_populates="post")

    tag = relationship("Tag", secondary='post_tag', back_populates="post")

    likes = relationship('PostLike', backref='post', lazy='dynamic')


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    text = Column(String)
    is_active = Column(Boolean, default=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())

    parent_id = Column(Integer, ForeignKey('comment.id'))
    replies = relationship('Comment', backref=backref('parent', remote_side=[id]))

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="comment")

    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post", back_populates="comment")


class PostLike(Base):
    __tablename__ = 'post_like'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    post_id = Column(Integer, ForeignKey('post.id'))


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(50))
    date_created = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship('Post', secondary="post_tag", back_populates='tag')


post_tag = Table(
    'post_tag', Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
)
