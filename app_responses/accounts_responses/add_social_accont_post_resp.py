from pydantic import BaseModel


class AddSocialAccountPostResponse(BaseModel):
    message: str
    status_code: int
