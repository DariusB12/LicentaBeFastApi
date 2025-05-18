from pydantic import BaseModel


class ProfileDetectionResponse(BaseModel):
    message: str
    status_code: int

    profile_photo: str | None  # THE IMAGE IS REPRESENTED AS base64
    username: str | None
    description: str | None
    no_followers: int | None
    no_following: int | None
    no_of_posts: int | None
