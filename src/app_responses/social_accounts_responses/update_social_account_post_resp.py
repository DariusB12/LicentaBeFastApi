from typing import List

from pydantic import BaseModel


class PostCommentUpdate(BaseModel):
    id: int
    comment: str


class PostPhotoUpdate(BaseModel):
    id: int
    photo_filename: str


class UpdateSocialAccountPostNotify(BaseModel):
    id: int
    description: str
    no_likes: int
    no_comments: int
    date_posted: str

    comments: List[PostCommentUpdate]
    photos: List[PostPhotoUpdate]

    profileId: int


class UpdateSocialAccountPostResponse(BaseModel):
    message: str
    status_code: int
