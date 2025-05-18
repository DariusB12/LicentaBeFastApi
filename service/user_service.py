from sqlalchemy.orm import Session

from exceptions.custom_exceptions import CustomHTTPException
from repo.user_repo import get_user_by_username, create_user, get_users_accounts
from fastapi import status


def accounts_dto_list(username: str, db: Session):
    """
    Returns a list of all dto accounts associated with the user
    :param username: the username of the user
    :param db: the db connection
    :return: the lis with all the accounts associated with the user
    """
    # Returns the newly created token
    return get_users_accounts(username, db)
