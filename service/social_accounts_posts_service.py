import os
from sqlalchemy.orm import Session

from app_requests.accounts_requests.add_social_account_post_req import AddSocialAccountPostReq
from logging_config import logger
from repo.social_account_post_repo import add_social_account_post, delete_social_account_post
from repo.social_account_repo import mark_social_account_as_modified
from service.utils.photos_utils import save_profile_photo
from validator.social_accounts_post_validator import validate_social_account_post

STORAGE_DIR = os.getenv("STORAGE_DIR")


def add_social_account_post_service(social_account_post: AddSocialAccountPostReq, db: Session):
    """
    Adds a post to the specified social account id in the AddSocialAccountPostReq entity
    :param social_account_post: post to be added
    :param db: the db connection
    :return: the added social account

    Throws HTTP 422 Unprocessable Content if the given post is invalid
    """
    logger.info('add social account post')
    # VALIDATE THE POST
    validate_social_account_post(social_account_post)

    # SAVE THE POST PHOTOS ON THE FILESYSTEM, THEN PASS TO REPO THE FILE_PATH OF THE POST PHOTOS
    post_photos_paths = []
    for photo_base64 in social_account_post.photos:
        photo_path = save_profile_photo(photo_base64)
        post_photos_paths.append(photo_path)

    created_post = add_social_account_post(social_account_post.description,
                                           social_account_post.noLikes,
                                           social_account_post.noComments,
                                           social_account_post.datePosted,
                                           social_account_post.comments,
                                           post_photos_paths,
                                           social_account_post.social_account_id
                                           , db)
    # IF NEW POST IS ADDED TO THE SOCIAL MEDIA ACCOUNT, THEN MARK IT AS MODIFIED
    mark_social_account_as_modified(social_account_post.social_account_id, db)
    return created_post


def delete_social_account_post_service(post_id: int, user_id: int, db: Session):
    """
    Delete the post based on the given id and deletes all the photos of the post from the system
    :param user_id: the id of the current user
    :param post_id:  the id of the post to delete
    :param db: the db connection
    :return: None
    Throws
        -HTTP_400_BAD_REQUEST if the id of the post doesn't exist or if the post doesn't belong to the current user
    """
    logger.info(f"delete post, id:{post_id}")

    filenames = delete_social_account_post(post_id, user_id, db)

    for filename in filenames:
        try:
            os.remove(STORAGE_DIR + '\\' + filename)
        except FileNotFoundError:
            logger.error('filename:', filename, ' not found')
