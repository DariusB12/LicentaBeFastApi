from sqlalchemy.orm import Session

from exceptions.custom_exceptions import CustomHTTPException
from repo.user_repo import get_user_by_username, create_user, delete_user
from security.jwt_token import create_access_token
from security.password_hash import verify_password, hash_password
from fastapi import status
from model.entities import User
from validator.auth_validator import validate_signup


def login(username: str, password: str, db: Session):
    """
    Verifies if the credentials are valid and returns a token
    :param db: the database connection
    :param username: username of the account
    :param password: password of the account
    :return: the token if the credentials are valid, otherwise throws an HTTPException 400 BAD_REQUEST
    """
    # Verify the user based on it's username
    user = get_user_by_username(username, db)

    # Throws exception if the user doesn't exist or if the password is incorrect
    if not user or not verify_password(password, user.hashed_password):
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid credentials"
        )

    # Returns the newly created token
    return create_access_token(data={"sub": user.username})


def signup(username: str, password: str, db: Session):
    """
    Registers a new user with the provided credentials
    :param db: the database connection
    :param username: the username of the account to be created
    :param password: the password of the account to be created
    :return: none or throws
    - HTTP 409 Conflict if an account already exists with the provided username
    - HTTP 422 Unprocessable Content if the credentials are invalid
    """
    # Validates the provided signup input
    validate_signup(username, password)

    # Verify if an account with this username already exists
    user = get_user_by_username(username, db)
    if user:
        raise CustomHTTPException(
            status_code=status.HTTP_409_CONFLICT,
            message="Username already taken"
        )

    # Hash the password
    hashed_password = hash_password(password)

    # Creates a User object and saved it
    new_user = User(username=username, hashed_password=hashed_password)
    create_user(new_user, db)


def delete(username: str, password: str, db: Session):
    """
    Deletes the user's account based on the provided credentials
    :param db: the database connection
    :param username: the username of the account to be deleted
    :param password: the password of the account to be deleted
    :return: none or throws
    - HTTP 400 BAD_REQUEST if the credentials are not valid or if the user doesn't exist
    """
    # Verify if an account with this username exists
    user = get_user_by_username(username, db)
    if not user or not verify_password(password, user.hashed_password):
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid credentials"
        )

    delete_user(user, db)
