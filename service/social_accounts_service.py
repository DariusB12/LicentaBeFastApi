import os

from sqlalchemy.orm import Session

from app_requests.accounts_requests.add_social_account_req import AddSocialAccountReq
from app_requests.accounts_requests.update_social_account_req import UpdateSocialAccountReq
from app_responses.social_accounts_responses.get_social_account_resp import SocialAccountFull, PostFull, \
    PostPhotoFull, CommentFull
from logging_config import logger
from model.AnalysisDTO import AnalysisDTO
from model.entities import Post, SocialMediaAccount

from repo.social_account_repo import add_social_account, delete_social_account, get_user_social_account, \
    update_social_account_repo
from service.utils.photos_utils import save_profile_photo
from validator.social_accounts_validator import validate_social_account_add, validate_social_account_update

STORAGE_DIR = os.getenv("STORAGE_DIR")


def add_social_account_service(social_account: AddSocialAccountReq, user_id: int, db: Session):
    """
    Adds a social account to the given user
    :param social_account: social account to be added
    :param user_id: the users id to add the social account to
    :param db: the db connection
    :return: the added social account

    Throws HTTP 422 Unprocessable Content if social media account is invalid
    """
    logger.info('add social account')

    # VALIDATE THE SOCIAL ACCOUNT
    validate_social_account_add(social_account)

    # SAVE THE PHOTO ON THE FILESYSTEM, THEN PASS TO REPO THE FILE_PATH OF THE PROFILE PHOTO
    photo_path = save_profile_photo(social_account.profile_photo)

    social_acc_created = add_social_account(social_account.username,
                                            social_account.profile_description,
                                            social_account.no_followers,
                                            social_account.no_following,
                                            social_account.no_of_posts,
                                            photo_path,
                                            user_id, db)

    return social_acc_created


def delete_social_account_service(social_account_id: int, user_id: int, db: Session):
    """
    Delete the social account based on the given id and deletes all the photos of the account from the system
    :param user_id: the id of the current user
    :param social_account_id: the id of the social account to be deleted
    :param db: the db connection
    :return: None
        Throws HTTP_400_BAD_REQUEST if the id of the social account doesn't exist or if it doesn't belong to the user
    """
    logger.info(f"delete social account, id:{social_account_id}")

    filenames = delete_social_account(social_account_id, user_id, db)

    for filename in filenames:
        try:
            os.remove(STORAGE_DIR + '\\' + filename)
        except FileNotFoundError:
            logger.error('filename:', filename, ' not found')


def get_user_social_account_full_entity(social_account_id: int, user_username: str, db: Session):
    """
    Gets the social media account of the user based on the give social account id

    :param social_account_id: the social account id
    :param user_username: the username of the user
    :param db: the db connection
    :return: the social account entity with all the attributes
    Throws:
    -HTTP 400 BAD_REQUEST if the user doesn't exist
                                the social account doesn't exist
                                or the social account doesn't belong to the user
    """
    social_account_db = get_user_social_account(social_account_id, user_username, db)

    # CREATE THE SocialAccountFull ENTITY FROM THE RETRIEVED ACCOUNT FROM DB
    # COMPOSE THE POST WITH THE COMMENTS AND PHOTOS ENTITIES IN FULL
    social_account_posts = []
    for post in social_account_db.posts:
        photos_full = []
        for photo in post.photos:
            photo_full = PostPhotoFull(
                id=photo.id,
                post_photo_filename=photo.post_photo_filename
            )
            photos_full.append(photo_full)
        comments_full = []
        for comment in post.comments:
            comment_full = CommentFull(
                id=comment.id,
                content=comment.content
            )
            comments_full.append(comment_full)

        post_full = PostFull(
            id=post.id,
            description=post.description,
            noLikes=post.noLikes,
            noComments=post.noComments,
            datePosted=post.datePosted.isoformat(),
            photos=photos_full,
            comments=comments_full
        )
        social_account_posts.append(post_full)

    # TODO: DACA FAC ANALIZA, O INSTANTIEZ AICI CU ATRIBUTELE
    if not social_account_db.analysis:
        # THE ACCOUNT DOESN'T HAVE AN ANALYSIS
        analysis_full = None
    else:
        analysis_full = AnalysisDTO(
            id=social_account_db.analysis.id,
            interest_domains=social_account_db.analysis.interest_domains,
            hobbies=social_account_db.analysis.hobbies,

            general_emotions=social_account_db.analysis.general_emotions,
            personality_types=social_account_db.analysis.personality_types,
            big_five_model=social_account_db.analysis.big_five_model,

            creationDate=social_account_db.analysis.creationDate.isoformat(),

            social_account_id=social_account_db.analysis.social_account_id
        )

    social_account = SocialAccountFull(
        id=social_account_db.id,
        username=social_account_db.username,
        profile_description=social_account_db.profile_description,
        profile_photo_filename=social_account_db.profile_photo_filename,
        no_followers=social_account_db.no_followers,
        no_following=social_account_db.no_following,
        no_of_posts=social_account_db.no_of_posts,
        modified=social_account_db.modified,

        posts=social_account_posts,
        analysis=analysis_full
    )

    return social_account


def update_social_account(social_account: UpdateSocialAccountReq, user_id: int, db: Session) -> SocialMediaAccount:
    """
    Updates a social account
    :param social_account: the social account to be updated
    :param user_id: the current user id
    :param db: the db connection
    :return: the updated social account

    Throws:
         -HTTP 400 BAD_REQUEST if social media account doesn't belong to the current user or if it doesn't exist
         -HTTP 422 Unprocessable Content if social media account is invalid
    """
    logger.info('update social account')

    # VALIDATE THE SOCIAL ACCOUNT
    validate_social_account_update(social_account)

    # SAVE THE PHOTO ON THE FILESYSTEM, THEN PASS TO REPO THE FILE_PATH OF THE PROFILE PHOTO
    photo_path = save_profile_photo(social_account.profile_photo)

    social_acc_updated, old_photo_filename = update_social_account_repo(
        social_account.id,
        social_account.username,
        social_account.profile_description,
        social_account.no_followers,
        social_account.no_following,
        social_account.no_of_posts,
        photo_path,
        user_id, db)
    try:
        os.remove(STORAGE_DIR + '\\' + old_photo_filename)
    except FileNotFoundError:
        logger.error('filename:', old_photo_filename, ' not found')

    return social_acc_updated
