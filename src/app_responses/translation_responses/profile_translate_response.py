from pydantic import BaseModel


class ProfileTranslationResponse(BaseModel):
    message: str
    status_code: int

    description: str
