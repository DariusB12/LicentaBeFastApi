from typing import List

from pydantic import BaseModel

from app_requests.translation_requests.post_comment_translation import PostCommentTranslation


class PostTranslationResponse(BaseModel):
    message: str
    status_code: int

    comments: List[PostCommentTranslation]
    description: str
