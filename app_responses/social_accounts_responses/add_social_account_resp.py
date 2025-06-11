from pydantic import BaseModel


class AddSocialAccountResponse(BaseModel):
    message: str
    status_code: int
    id: int
