from typing import List
from pydantic import BaseModel


class PostComment(BaseModel):
    id: int
    comment: str


class PostPhoto(BaseModel):
    id: int
    photo_url: str


class UpdateSocialAccountPostReq(BaseModel):
    id: int
    description: str
    no_likes: int
    no_comments: int
    date_posted: str
    comments: List[PostComment]
    photos: List[PostPhoto]
