from typing import List

from pydantic import BaseModel


class PostComment(BaseModel):
    id: int
    comment: str


class PostPhoto(BaseModel):
    id: int
    photo_filename: str


class AddSocialAccountPostNotify(BaseModel):
    id: int
    description: str
    no_likes: int
    no_comments: int
    date_posted: str

    comments: List[PostComment]
    photos: List[PostPhoto]

    profileId: int


class AddSocialAccountPostResponse(BaseModel):
    message: str
    status_code: int
