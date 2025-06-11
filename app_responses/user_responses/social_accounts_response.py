from typing import List
from pydantic import BaseModel


class SocialAccount(BaseModel):
    id: int
    username: str
    profile_photo_filename: str
    no_followers: int
    no_following: int
    no_of_posts: int
    analysed: bool


class SocialAccountsResponse(BaseModel):
    message: str
    status_code: int

    social_accounts: List[SocialAccount]
