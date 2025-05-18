from pydantic import BaseModel


class ProfileDetectionRequest(BaseModel):
    image: str
