from pydantic import BaseModel


class UpdateSocialAccountReq(BaseModel):
    id: int
    username: str
    profile_description: str
    no_followers: int
    no_following: int
    no_of_posts: int
    profile_photo: str
