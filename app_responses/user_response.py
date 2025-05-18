from pydantic import BaseModel
from typing import List
from dtos.social_account_dto import SocialAccountDTO


class UserResponse(BaseModel):
    message: str
    accounts: List[SocialAccountDTO]
    status_code: int
