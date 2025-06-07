from pydantic import BaseModel


class AddSocialAccountReq(BaseModel):
    username: str
    profile_description: str
    no_followers: int
    no_following: int
    no_of_posts: int
    profile_photo: str  # receive the image in base64 form frontend when adding it
