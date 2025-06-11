from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from app_requests.translation_requests.post_translate_request import PostTranslationRequest
from app_requests.translation_requests.profile_translate_request import ProfileTranslationRequest
from app_responses.translation_responses.post_translate_response import PostTranslationResponse
from app_responses.translation_responses.profile_translate_response import ProfileTranslationResponse
from logging_config import logger
from model.entities import User
from security.jwt_token import verify_token
from service.translation_service import detect_lang_and_translate_to_english, \
    translate_post_to_english

router = APIRouter(prefix="/translate", tags=["Translate_API"])


@router.post("/profile")
def translate_profile_data(profile: ProfileTranslationRequest, user: User = Depends(verify_token)):
    """
    Translates the description of a profile in English.
    If the description is empty, then the response will be the same text

    IF THE TRANSLATION OF THE TEXT IS MADE FROM ENG TO ENG THEN THE TEXT QUALITY MAY IMPROVE
    (e.g I am going tod shopd => I am going to shop)

    :param profile: Profile object
    :param user: used as dependency for token validation
    :return: the translated description

    Throws CustomHTTPException 403 FORBIDDEN if the user doesn't exist (invalid token)
    """
    logger.info('Translate profile')
    description = detect_lang_and_translate_to_english(profile.description)

    response = ProfileTranslationResponse(
        message="Profile data translated with success",
        status_code=200,
        description=description
    )
    return JSONResponse(status_code=200, content=response.dict())


@router.post("/post")
def translate_post_data(post: PostTranslationRequest, user: User = Depends(verify_token)):
    """
    Translates the description and comments of a post in English
    If the description is empty then the same text will be returned
    The same logic is applied to the comments, but if any comment is empty before or after the translation, then the
    response list with the comments will not contain these comments.
    The id's of the comments will be returned unmodified

    IF THE TRANSLATION OF THE TEXT IS MADE FROM ENG TO ENG THEN THE TEXT QUALITY MAY IMPROVE
    (e.g I am going tod shopd => I am going to shop)

    :param post: Post object
    :param user: used as dependency for token validation
    :return: the translated description and comments

    Throws CustomHTTPException 403 FORBIDDEN if the user doesn't exist (invalid token)
    """
    logger.info('Translate post')

    description, comments = translate_post_to_english(post)

    response = PostTranslationResponse(
        message="Post data translated with success",
        status_code=200,

        description=description,
        comments=comments
    )
    return JSONResponse(status_code=200, content=response.dict())
