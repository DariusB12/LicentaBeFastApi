from pydantic import BaseModel


class AuthResponse(BaseModel):
    message: str
    status_code: int
    token: str = None
