import os
from typing import List

from sqlalchemy.orm import Session

from app_requests.accounts_requests.add_social_account_post_req import AddSocialAccountPostReq
from app_requests.accounts_requests.update_social_account_post_req import UpdateSocialAccountPostReq, PostPhoto
from logging_config import logger
from model.entities import Post
from repo.social_account_post_repo import add_social_account_post, delete_social_account_post, \
    update_social_account_post
from service.utils.photos_utils import save_profile_photo
from validator.social_accounts_post_validator import validate_social_account_post_add, \
    validate_social_account_post_update

STORAGE_DIR = os.getenv("STORAGE_DIR")


def add_social_account_post_service(social_account_post: AddSocialAccountPostReq, user_id: int, db: Session):
    """
    Adds a post to the specified social account id in the AddSocialAccountPostReq entity
    :param user_id: the id of the current user
    :param social_account_post: post to be added
    :param db: the db connection
    :return: the added post

    Throws
        -HTTP 422 Unprocessable Content if the given post is invalid
        -HTTP 400 BAD_REQUEST if trying to add post to a social account that doesn't exist
                                    or doesn't belong to the current user
    """
    logger.info('add social account post')
    # VALIDATE THE POST
    validate_social_account_post_add(social_account_post)

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
                                           social_account_post.social_account_id,
                                           user_id, db)
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


def update_social_account_post_service(post_to_update: UpdateSocialAccountPostReq, user_id: int, db: Session) -> Post:
    """
    Updates a post to the specified social account id in the AddSocialAccountPostReq entity
    :param user_id: the current user id
    :param post_to_update: the post entity to update
    :param db: the db connection
    :return: the updated post

    Throws
        -HTTP 422 Unprocessable Content if the given post is invalid
        -HTTP 400 BAD_REQUEST if the post doesn't belong to the current user
                                if the post doesn't exist
                                if the date of the post could not be parsed
    """
    logger.info('update post')
    # VALIDATE THE POST
    validate_social_account_post_update(post_to_update)

    # SAVE THE POST PHOTOS ON THE FILESYSTEM, THEN PASS TO REPO THE POST PHOTOS WITH FILE_PATHS
    post_photos_with_filenames: List[PostPhoto] = []
    for photo in post_to_update.photos:
        photo_path = save_profile_photo(photo.photo_url)
        post_photos_with_filenames.append(PostPhoto(
            id=photo.id,
            photo_url=photo_path
        ))

    updated_post, old_photos_filenames = update_social_account_post(post_to_update.id,
                                                                    post_to_update.description,
                                                                    post_to_update.no_likes,
                                                                    post_to_update.no_comments,
                                                                    post_to_update.date_posted,
                                                                    post_to_update.comments,
                                                                    post_photos_with_filenames,
                                                                    user_id, db)

    for old_filename in old_photos_filenames:
        try:
            os.remove(STORAGE_DIR + '\\' + old_filename)
        except FileNotFoundError:
            logger.error('filename:', old_filename, ' not found')

    return updated_post
