from typing import List
from pydantic import BaseModel


class AddSocialAccountPostReq(BaseModel):
    description: str
    noLikes: int
    noComments: int
    datePosted: str
    comments: List[str]
    photos: List[str]
    social_account_id: int
