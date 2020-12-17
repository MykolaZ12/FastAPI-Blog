from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from slugify import slugify
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.article import schemas
from .models import PostLike, Tag, Post, Comment, Category
from app.base.crud import CRUDBase


class CRUDPost(CRUDBase[Post, schemas.PostCreate, schemas.PostUpdate]):
    """CRUD for Post"""

    def create_with_tags_and_category(self, db: Session, *,
                                      post_schema: schemas.PostCreate) -> Post:
        """Create post with user and tags"""
        tags = tag_crud.get_or_create_tag_objects(db=db, tags=post_schema.tag)
        category = category_crud.get(db=db, id=post_schema.category)
        data = jsonable_encoder(post_schema, exclude={"tag", "category"})
        print(tags)
        print(category)
        db_post = self.model(**data, tag=tags, category=category)
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

    def get_or_create_tag_objects(self, db: Session, tags: List[str]) -> List[Tag]:
        """
        Get list objects Tag or/and create objects Tag if tags does not existing in DB
        """
        tag_obj_list = db.query(self.model).filter(self.model.name.in_(tags)).all()
        # finding the difference between existing tags and non-existent tags
        difference = list(set([tag.name for tag in tag_obj_list]) ^ set([tag for tag in tags]))
        # create new Tag objects in list
        if difference:
            for element in difference:
                tag_obj_list.append(Tag(name=element))
        return tag_obj_list


class CRUDCategory(CRUDBase[Category, schemas.CategoryCreate, schemas.CommentUpdate]):
    pass


# create CRUD object for posts
post_crud = CRUDPost(Post)

# create CRUD object for comments
comment_crud = CRUDComment(Comment)

# create CRUD object for tags
tag_crud = CRUDTag(Tag)

# create CRUD object for categories
category_crud = CRUDCategory(Category)


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
                 tag: Optional[List[str]] = None, category: int = None):
    """
    Filter Post by title, text, tag and category
    """
    list_filters = []
    if search:
        list_filters.append(Post.title.match(search))
        list_filters.append(Post.text.match(search))
    if tag:
        list_filters.append(Tag.name.in_(tag))
    if category:
        list_filters.append(Post.category_id == category)

    filtered_posts = db.query(Post) \
        .filter(or_(*list_filters)) \
        .join(Post.tag) \
        .order_by(Post.date_created.desc()) \
        .offset(skip) \
        .limit(limit) \
        .all()
    return filtered_posts


def generate_slug(text: str):
    return slugify(text)
