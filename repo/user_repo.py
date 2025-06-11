from typing import List

from starlette import status

from app_responses.user_responses.social_accounts_response import SocialAccount
from exceptions.custom_exceptions import CustomHTTPException
from logging_config import logger
from model.entities import User
from sqlalchemy.orm import Session


def get_user_by_username(username: str, db: Session):
    """
    Returns the user with the given username
    :param username: the user's username
    :param db: the database connection
    :return: the user with the given username if exists, otherwise None
    """
    user = db.query(User).filter(User.username == username).first()
    return user


def create_user(user: User, db: Session):
    """
    Creates a new user in the database.
    :param user: the user object to create
    :param db: the database connection
    :return: none
    """
    db.add(user)
    db.commit()
    db.flush()


def collect_user_photo_paths(user: User) -> list[str]:
    """
    Gathers all file paths associated with a user:
    - Profile photo paths from SocialMediaAccount
    - Post photo paths from PostPhoto
    """
    filenames = []

    for account in user.social_accounts:
        # Profile photo
        if account.profile_photo_filename:
            filenames.append(account.profile_photo_filename)

        # Post photos
        for post in account.posts:
            for photo in post.photos:
                if photo.post_photo_filename:
                    filenames.append(photo.post_photo_filename)

    return filenames


def delete_user(user: User, db: Session):
    """
    Deletes the user from the database and returns a list of photo filenames to be deleted from storage.
    :param user: the user object to be deleted
    :param db: the database connection
    :return: a list of photo filenames to be deleted from storage
    """
    filenames = collect_user_photo_paths(user)

    db.delete(user)
    db.commit()
    db.flush()

    return filenames


def get_social_accounts(username: str, db: Session) -> List[SocialAccount]:
    """
    Gets all the social accounts of the given user_id from the database
    :param username: the user's username
    :param db: the db connection
    :return: list with all social accounts of the user
    Throws 400 BAD_REQUEST if the user doesn't exist
    """
    # Verify if an account with this username exists
    user = get_user_by_username(username, db)
    if not user:
        logger.error('User does not exist')
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="User does not exist"
        )
    social_accounts = []
    for social_account in user.social_accounts:
        social_accounts.append(SocialAccount(
            id=social_account.id,
            username=social_account.username,
            profile_photo_filename=social_account.profile_photo_filename,
            no_followers=social_account.no_followers,
            no_following=social_account.no_following,
            no_of_posts=social_account.no_of_posts,
            analysed=bool(social_account.analysis)
        ))
    return social_accounts
