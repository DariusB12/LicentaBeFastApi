from typing import List
from pydantic import BaseModel
from app_requests.translation_requests.post_comment_translation import PostCommentTranslation


class PostTranslationRequest(BaseModel):
    comments: List[PostCommentTranslation]
    description: str
