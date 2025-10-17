from pydantic import BaseModel


class UpdateSocialAccountNotify(BaseModel):
    id: int
    username: str
    profile_description: str
    no_followers: int
    no_following: int
    no_of_posts: int
    profile_photo: str
    modified: bool


class UpdateSocialAccountResponse(BaseModel):
    message: str
    status_code: int

