from sqlalchemy.orm import Session

from app_requests.accounts_requests.add_social_account_post_req import AddSocialAccountPostReq
from repo.social_account_post_repo import add_social_account_post
from service.utils.photos_utils import save_profile_photo
from validator.social_accounts_post_validator import validate_social_account_post


def add_social_account_post_service(social_account_post: AddSocialAccountPostReq, db: Session):
    """
    Adds a post to the specified social account id in the AddSocialAccountPostReq entity
    :param social_account_post: post to be added
    :param db: the db connection
    :return: the id of the added social account

    Throws HTTP 422 Unprocessable Content if the given post is invalid
    """
    # VALIDATE THE POST
    validate_social_account_post(social_account_post)

    # SAVE THE POST PHOTOS ON THE FILESYSTEM, THEN PASS TO REPO THE FILE_PATH OF THE POST PHOTOS
    post_photos_paths = []
    for photo_base64 in social_account_post.photos:
        photo_path = save_profile_photo(photo_base64)
        post_photos_paths.append(photo_path)

    # TODO: PENTRU POST CREATED UPDATE WEBSOCKET, created_post RETURNAT E FARA ATRIBUTELE COMMENTS SI PHOTOS
    created_post = add_social_account_post(social_account_post.description,
                                           social_account_post.noLikes,
                                           social_account_post.noComments,
                                           social_account_post.datePosted,
                                           social_account_post.comments,
                                           post_photos_paths,
                                           social_account_post.social_account_id
                                           , db)
