from pydantic import BaseModel


class SocialAccountDTO(BaseModel):
    id: int
    username: str
    profile_photo: str  # Base64-encoded image string
    no_followers: int
    no_following: int
    no_of_posts: int
    analysed: bool
