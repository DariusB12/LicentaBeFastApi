from pydantic import BaseModel


class DeleteSocialAccountResponse(BaseModel):
    message: str
    status_code: int
