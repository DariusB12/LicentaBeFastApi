from datetime import datetime

from sqlalchemy.orm import Session
from starlette import status

from exceptions.custom_exceptions import CustomHTTPException
from logging_config import logger
from model.AnalysisDTO import AnalysisDTO
from model.entities import SocialMediaAccount, User, Analysis


def add_social_account(username, profile_description, no_followers, no_following, no_of_posts, photo_path,
                       user_id: int, db: Session):
    """
    Adds a new social account into the database to the given user
    :param username: the username of the social account
    :param profile_description: the description of the social account
    :param no_followers: the no followers of the social account
    :param no_following: the no following of the social account
    :param no_of_posts: the no posts of the social account
    :param photo_path: the profile photo path of the social account
    :param user_id: the user id of the social account to be added
    :param db: the database session
    :return: the social media created account
    """
    new_account = SocialMediaAccount(
        user_id=user_id,
        username=username,
        profile_description=profile_description,
        no_followers=no_followers,
        no_following=no_following,
        no_of_posts=no_of_posts,
        profile_photo_filename=photo_path,
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)  # Ensures all DB-generated fields are available

    return new_account


def delete_social_account(social_account_id: int, user_id: int, db: Session):
    """
    Delete the given social media account from the database
    :param user_id: the id of the current user
    :param social_account_id: the id of the social account to be deleted
    :param db: the db connection
    :return: a list with all the photo filenames of the social account to be deleted from system
    Throws HTTP_400_BAD_REQUEST if the id of the social account doesn't exist or if it doesn't belong to the given user
    """
    # Verify if an account with this id exists
    social_media_account = db.query(SocialMediaAccount).join(User).filter(User.id == user_id,
                                                                          SocialMediaAccount.id == social_account_id).first()

    if not social_media_account:
        logger.error("Social account does not exist or it doesn't belong to the given user")
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Social account does not exist or it doesn't belong to the given user"
        )

    filenames = []
    if social_media_account.profile_photo_filename:
        filenames.append(social_media_account.profile_photo_filename)
    # Posts photos
    for post in social_media_account.posts:
        for photo in post.photos:
            if photo.post_photo_filename:
                filenames.append(photo.post_photo_filename)

    db.delete(social_media_account)
    db.commit()
    db.flush()

    return filenames


def get_user_social_account(social_account_id: int, user_username: str, db: Session):
    """
    Retrieve the social account from the database
    :param social_account_id: the social account id
    :param user_username: the username of the user to retrieve the social account from
    :param db: the db connection
    :return: social account entity retrieved from db
    Throws:
        -HTTP_400_BAD_REQUEST if the user/social_account doesn't exist or the social account doesn't belong to the user
    """
    # VERIFY THE ACCOUNT BELONGS TO THE GIVEN USER
    social_account_db = db.query(SocialMediaAccount).join(User).filter(
        User.username == user_username, SocialMediaAccount.id == social_account_id).first()

    if not social_account_db:
        logger.error("Social account does not exist or it doesn't correspond to the given user")
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Social account does not exist or it doesn't correspond to the given user"
        )

    return social_account_db


def update_social_account_repo(account_id: int, username, profile_description, no_followers, no_following, no_of_posts,
                               photo_path, user_id: int, db: Session) -> (SocialMediaAccount, str):
    """
    Updates a new social account
    :param account_id: the id if the account to be updated
    :param username: the username of the social account
    :param profile_description: the description of the social account
    :param no_followers: the no followers of the social account
    :param no_following: the no following of the social account
    :param no_of_posts: the no posts of the social account
    :param photo_path: the profile photo path of the social account
    :param user_id: the user id of the social account to be added
    :param db: the database session
    :return: the social media created account
    Throws:
             -HTTP 400 BAD_REQUEST if social media account doesn't belong to the current user or if it doesn't exist
    """
    account = db.query(SocialMediaAccount).filter(
        SocialMediaAccount.id == account_id,
        SocialMediaAccount.user_id == user_id
    ).first()

    if not account:
        logger.error("Social account does not exist or it doesn't correspond to the given user")
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Social account does not exist or it doesn't correspond to the given user"
        )

    old_photo_filename = account.profile_photo_filename

    account.username = username
    account.profile_description = profile_description
    account.no_followers = no_followers
    account.no_following = no_following
    account.no_of_posts = no_of_posts
    account.profile_photo_filename = photo_path
    account.modified = True

    db.commit()
    db.refresh(account)  # Ensures all DB-generated fields are available

    return account, old_photo_filename


def add_social_account_analysis_repo(analysis: AnalysisDTO, username: str, db: Session):
    """
    Adds the analysis to the social account specified inside the analysis object
    :param username: the current user username
    :param analysis: the analysis to be added
    :param db: the db connection
    :return: the id of the created analysis
    Throws
        -HTTP 400 BAD_REQUEST if the social account does not exist
                                or if it doesn't belong to the current user
    """

    # VERIFY IF THE SOCIAL ACCOUNT EXISTS
    account = db.query(SocialMediaAccount).join(User).filter(
        User.username == username, SocialMediaAccount.id == analysis.social_account_id).first()

    if not account:
        logger.error("Social account does not exist or it doesn't correspond to the given user")
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Social account does not exist or it doesn't correspond to the given user"
        )

    # DELETE THE PREVIOUS ANALYSIS BEFORE SAVING THE NEW ONE
    analysis_db = db.query(Analysis).join(SocialMediaAccount).filter(
        Analysis.social_account_id == analysis.social_account_id
    ).first()

    if analysis_db:
        db.delete(analysis_db)
        db.flush()

    # MARK THE SOCIAL ACCOUNT AS NOT MODIFIED (NOT MODIFIED AFTER THE ANALYSIS WAS MADE)
    account.modified = False
    db.add(account)

    # the AnalysisDTO object is used for indicating the attributes of the entity
    # but for the date attribute, we consider the creationDate=datetime.now()
    analysis_db_entity = Analysis(
        interest_domains=analysis.interest_domains,
        hobbies=analysis.hobbies,
        general_emotions=analysis.general_emotions,
        personality_types=analysis.personality_types,
        big_five_model=analysis.big_five_model,
        creationDate=datetime.now(),
        social_account_id=analysis.social_account_id
    )

    db.add(analysis_db_entity)
    db.commit()
    db.refresh(analysis_db_entity)  # Optional: refresh to get any generated IDs if needed

    return analysis_db_entity.id
