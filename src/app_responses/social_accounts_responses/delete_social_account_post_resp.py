from pydantic import BaseModel


class DeleteSocialAccountPostResponse(BaseModel):
    message: str
    status_code: int
