from pydantic import BaseModel


class PostDetectionRequest(BaseModel):
    image: str
