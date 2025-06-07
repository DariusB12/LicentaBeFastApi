from pydantic import BaseModel


class PostCommentTranslation(BaseModel):
    id: int
    comment: str
