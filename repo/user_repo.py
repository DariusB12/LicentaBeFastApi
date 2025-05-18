from typing import List
from dtos.social_account_dto import SocialAccountDTO
from model.entities import User
from sqlalchemy.orm import Session


def get_user_by_username(username: str, db: Session):
    """
    Returns the user with the given username
    :param username: the user's username
    :param db: the database connection
    :return: the user with the given username if exists, otherwise None
    """
    return db.query(User).filter(User.username == username).first()


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


def delete_user(user: User, db: Session):
    """
    Deletes the user from the database.
    :param user: the user object to be deleted
    :param db: the database connection
    :return: none
    """
    db.delete(user)
    db.commit()
    db.flush()


def get_users_accounts(username: str, db: Session) -> List[SocialAccountDTO]:
    """
    Returns a list of all the social accounts (DTOs) of the given username
    :param username: the user's username
    :param db: the database connection
    :return: a list with all the social media accounts of the given username
    """
    # Extract the user based on the provided username
    user = db.query(User).filter(User.username == username).first()

    # If the user doesn't exist, return an empty list
    if not user:
        return []

    # Get all the user's social media accounts
    accounts = user.social_accounts

    return [
        SocialAccountDTO(
            id=account.id,
            username=account.username,
            profile_photo=account.profile_photo,
            no_followers=account.no_followers,
            no_following=account.no_following,
            no_of_posts=account.no_of_posts,
            analysed=False,
        )
        for account in accounts
    ]

