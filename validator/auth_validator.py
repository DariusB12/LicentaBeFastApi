from fastapi import status
from exceptions.custom_exceptions import CustomHTTPException
from logging_config import logger


def validate_signup(username: str, password: str):
    """
    Validates the signup input data
    (username and password should be >=3 in length and cannot contain only white spaces)
    :param username: the provided username
    :param password: the provided password
    :return: none or throws HTTP 422 UNPROCESSABLE_ENTITY if the username or password are invalid
    """
    if not username or username.strip() == "":
        logger.error('Username cannot be empty or just spaces')
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Username cannot be empty or just spaces."
        )
    if len(username.strip()) < 3:
        logger.error('Username must be at least 3 characters long')
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Username must be at least 3 characters long."
        )

    if not password or password.strip() == "":
        logger.error("Password cannot be empty or just spaces")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Password cannot be empty or just spaces."
        )
    if len(password.strip()) < 3:
        logger.error("Password must be at least 3 characters long")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Password must be at least 3 characters long."
        )
