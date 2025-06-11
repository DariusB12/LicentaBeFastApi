from fastapi import status

from app_requests.accounts_requests.add_social_account_post_req import AddSocialAccountPostReq
from exceptions.custom_exceptions import CustomHTTPException
from datetime import datetime

from logging_config import logger


def validate_social_account_post(post: AddSocialAccountPostReq):
    """
    Validate that all required fields in social_account_post are present and valid.
    - description can be empty
    - noLikes and noComments must be >= -1
    - datePosted must be a non-empty string and in ISO format (YYYY-MM-DD)
    - comments and photos must be lists (can be empty)
    - social_account_id must be a positive integer
    :param post: the post to be validated
    :return: none
    throws HTTP 422 UNPROCESSABLE_ENTITY if the post is invalid
    """
    if post.noLikes is None or post.noLikes < -1:
        logger.error("Number of likes must be equal or greater than -1")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Number of likes must be equal or greater than -1."
        )

    if post.noComments is None or post.noComments < -1:
        logger.error("Number of comments must be equal or greater than -1")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Number of comments must be equal or greater than -1."
        )

    try:
        datetime.strptime(post.datePosted, "%Y-%m-%d")
    except ValueError:
        logger.error("Date must be in ISO format (YYYY-MM-DD)")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Date must be in ISO format (YYYY-MM-DD)."
        )

    if not isinstance(post.comments, list):
        logger.error("Comments must be a list")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Comments must be a list."
        )

    if not isinstance(post.photos, list):
        logger.error("Photos must be a list")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Photos must be a list."
        )

    if post.social_account_id is None or post.social_account_id < 0:
        logger.error("Social account ID must be a positive integer")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Social account ID must be a positive integer."
        )
