from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Comment
class CommentBase(BaseModel):
    text: str

    class Config:
        orm_mode = True


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass


class CommentInDB(CommentBase):
    post_id: int
    user_id: int


class CommentInResponse(CommentBase):
    id: int
    date_created: datetime
    replies: List['CommentInResponse'] = []


CommentInResponse.update_forward_refs()


# Tag
class TagBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    pass


class TagInDB(TagBase):
    pass


class TagInResponse(TagBase):
    id: int
    date_created: datetime


# Category
class CategoryBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryInDB(CategoryBase):
    user_id: int
    slug: str


class CategoryInResponse(CategoryBase):
    id: int
    slug: str
    date_created: datetime


# Post
class PostBase(BaseModel):
    title: str
    text: str

    class Config:
        orm_mode = True


class PostCreate(PostBase):
    category: int
    tag: Optional[List[str]] = None


class PostUpdate(PostBase):
    category: int
    tag: Optional[List[str]] = None


class PostInDB(PostBase):
    slug: str
    user_id: int
    category: int
    tag: Optional[List[str]] = None


class PostInResponse(PostBase):
    id: str
    date_created: datetime
    category: Optional[CategoryInResponse]
    tag: Optional[List[TagInResponse]] = None
    comment: Optional[List[CommentInResponse]] = None


# Like
class Like(BaseModel):
    id: int
    user_id: int
    post_id: int

    class Config:
        orm_mode = True
