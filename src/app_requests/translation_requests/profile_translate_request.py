from pydantic import BaseModel


class ProfileTranslationRequest(BaseModel):
    description: str
