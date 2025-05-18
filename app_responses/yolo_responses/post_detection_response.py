from pydantic import BaseModel


class PostDetectionResponse(BaseModel):
    message: str
    status_code: int

    post_photo: str | None  # THE IMAGE IS REPRESENTED AS base64
    description: str | None
    no_likes: int | None
    no_comments: int | None
    date: str | None  # THE IMAGE IS REPRESENTED AS base64
    comments: list
