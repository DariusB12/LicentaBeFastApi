from typing import List

from pydantic import BaseModel

from model.AnalysisDTO import AnalysisDTO


class PostPhotoFull(BaseModel):
    id: int
    post_photo_filename: str


class CommentFull(BaseModel):
    id: int
    content: str


class PostFull(BaseModel):
    id: int
    description: str
    noLikes: int
    noComments: int
    datePosted: str
    photos: List[PostPhotoFull]
    comments: List[CommentFull]


class SocialAccountFull(BaseModel):
    id: int
    username: str
    profile_description: str
    profile_photo_filename: str
    no_followers: int
    no_following: int
    no_of_posts: int
    modified: bool

    posts: List[PostFull]
    analysis: AnalysisDTO | None


class GetSocialAccountResponse(BaseModel):
    message: str
    status_code: int

    social_account: SocialAccountFull
