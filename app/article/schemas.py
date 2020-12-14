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


# Post
class PostBase(BaseModel):
    title: str
    text: str

    class Config:
        orm_mode = True


class PostCreate(PostBase):
    tag: Optional[List[TagCreate]] = None


class PostUpdate(PostBase):
    tag: Optional[List[TagCreate]] = None


class PostInDB(PostBase):
    slug: str
    user_id: int
    tag: Optional[List[TagCreate]] = None


class PostInResponse(PostBase):
    id: str
    date_created: datetime
    tag: Optional[List[TagInResponse]] = None
    comment: Optional[List[CommentInResponse]] = None
