from fastapi import status

from app_requests.accounts_requests.add_social_account_req import AddSocialAccountReq
from app_requests.accounts_requests.update_social_account_req import UpdateSocialAccountReq
from exceptions.custom_exceptions import CustomHTTPException
from logging_config import logger


def validate_social_account_add(social_account: AddSocialAccountReq):
    """
    Validate that all required fields in social_account entity for Add request are valid.
    No of followers/following/posts should be >=0 and not empty.
    Username and profile_photo cannot be empty.
    Only description can be empty.
    :param social_account: the account to be validated
    :return: none
    throws HTTP 422 UNPROCESSABLE_ENTITY if the social_account is invalid
    """
    if not social_account.username or social_account.username.strip() == "":
        logger.error("Username cannot be empty or just spaces")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Username cannot be empty or just spaces."
        )
    if social_account.no_followers is None or social_account.no_followers < 0:
        logger.error("Number of followers must be zero or positive")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Number of followers must be zero or positive."
        )

    if social_account.no_following is None or social_account.no_following < 0:
        logger.error("Number of following must be zero or positive")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Number of following must be zero or positive."
        )

    if social_account.no_of_posts is None or social_account.no_of_posts < 0:
        logger.error("Number of posts must be zero or positive")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Number of posts must be zero or positive."
        )

    if not social_account.profile_photo or social_account.profile_photo.strip() == "":
        logger.error("Profile photo cannot be empty")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Profile photo cannot be empty."
        )


def validate_social_account_update(social_account: UpdateSocialAccountReq):
    """
    Validate that all required fields in social_account entity for Update request are valid.
    No of followers/following/posts should be >=0 and not empty.
    Username and profile_photo cannot be empty.
    Only description can be empty.
    :param social_account: the account to be validated
    :return: none
    throws HTTP 422 UNPROCESSABLE_ENTITY if the social_account is invalid
    """
    if not social_account.username or social_account.username.strip() == "":
        logger.error("Username cannot be empty or just spaces")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Username cannot be empty or just spaces."
        )
    if social_account.no_followers is None or social_account.no_followers < 0:
        logger.error("Number of followers must be zero or positive")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Number of followers must be zero or positive."
        )

    if social_account.no_following is None or social_account.no_following < 0:
        logger.error("Number of following must be zero or positive")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Number of following must be zero or positive."
        )

    if social_account.no_of_posts is None or social_account.no_of_posts < 0:
        logger.error("Number of posts must be zero or positive")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Number of posts must be zero or positive."
        )

    if not social_account.profile_photo or social_account.profile_photo.strip() == "":
        logger.error("Profile photo cannot be empty")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Profile photo cannot be empty."
        )
