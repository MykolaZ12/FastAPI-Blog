from typing import List

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from slugify import slugify
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.article import schemas
from .models import PostLike, Tag, Post, Comment
from app.base.crud import CRUDBase


class CRUDPost(CRUDBase[Post, schemas.PostCreate, schemas.PostUpdate]):
    """CRUD for Post"""

    def create_with_tags(self, db: Session, *, post_schema: schemas.PostCreate) -> Post:
        """Create post with user and tags"""
        tags = tag_crud.get_or_create_tag_objects(db=db, tag_schema=post_schema.tag)
        data = jsonable_encoder(post_schema, exclude={"tag"})
        db_post = self.model(**data, tag=tags)
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post


class CRUDComment(CRUDBase[Comment, schemas.CommentCreate, schemas.CommentUpdate]):
    """CRUD for Comment"""

    def get_without_parent(self, db: Session, id: int):
        return db.query(self.model).filter_by(parent=None).filter(self.model.id == id).first()

    def get_multi_without_parent(self, db: Session, *, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter_by(parent=None).offset(skip).limit(limit).all()


class CRUDTag(CRUDBase[Tag, schemas.TagCreate, schemas.TagUpdate]):
    """CRUD for Tag"""

    def get_or_create_tag_objects(self, db: Session, tag_schema: List[schemas.TagCreate]
                                 ) -> List[Tag]:
        """
        Get list objects tags or/and create objects tags if tags does not existing in DB
        """
        list_filters = []
        for tag in tag_schema:
            list_filters.append(self.model.name == tag.name)
        tag_obj_list = db.query(self.model).filter(or_(*list_filters)).all()

        # finding the difference between existing tags and non-existent tags
        difference = list(set([t.name for t in tag_obj_list]) ^ set([t.name for t in tag_schema]))

        if difference:
            for element in difference:
                tag_obj_list.append(Tag(name=element))
        return tag_obj_list


# create CRUD object for posts
post_crud = CRUDPost(Post)

# create CRUD object for comments
comment_crud = CRUDComment(Comment)

# create CRUD object for tags
tag_crud = CRUDTag(Tag)


def like(db: Session, post_id: int, user_id: int):
    like_post = PostLike(user_id=user_id, post_id=post_id)
    db.add(like_post)
    db.commit()
    db.refresh(like_post)
    return like_post


def unlike(db: Session, post_id: int, user_id: int):
    unlike_post = db.query(PostLike).filter_by(user_id=user_id, post_id=post_id).first()
    db.delete(unlike_post)
    db.commit()
    return unlike_post


def count_likes(db: Session, post_id: int):
    count = db.query(PostLike).filter_by(post_id=post_id).count()
    return count


def has_liked_post(db: Session, post_id: int, user_id: int):
    return db.query(PostLike).filter_by(user_id=user_id, post_id=post_id).count() > 0


def post_filters(db: Session, skip: int = 0, limit: int = 100, search: str = None,
                 tag: list = None):
    list_filters = []
    if search:
        # add filter search by title
        list_filters.append(Post.title.match(search))
        # add filter search by text
        list_filters.append(Post.text.match(search))
    if tag:
        # add filter by tags
        for tag_name in tag:
            list_filters.append(Tag.name == tag_name)

    filtered_posts = db.query(Post) \
        .filter(or_(*list_filters)) \
        .order_by(Post.date_created.desc()) \
        .offset(skip) \
        .limit(limit) \
        .all()

    return filtered_posts


def generate_slug(text: str):
    return slugify(text)
