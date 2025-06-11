from typing import List

from sqlalchemy.orm import Session


from app_responses.user_responses.social_accounts_response import SocialAccount
from logging_config import logger
from repo.user_repo import get_social_accounts


def get_user_social_account(username: str, db: Session) -> List[SocialAccount]:
    """
    Gets all the social accounts of the given user

    :param username: the username of the user which we want to get the social accounts
    :param db: the database connection
    :return: list with all the social accounts
    or throws 400 BAD_REQUEST if the user doesn't exist
    """
    logger.info(f'get social accounts, username: {username}')
    social_accounts = get_social_accounts(username, db)

    return social_accounts
