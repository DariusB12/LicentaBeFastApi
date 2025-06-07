from sqlalchemy.orm import Session

from app_requests.accounts_requests.add_social_account_req import AddSocialAccountReq

from repo.social_account_repo import add_social_account
from service.utils.photos_utils import save_profile_photo
from validator.social_accounts_validator import validate_social_account


def add_social_account_service(social_account: AddSocialAccountReq, user_id: int, db: Session):
    """
    Adds a social account to the given user
    :param social_account: social account to be added
    :param user_id: the users id to add the social account to
    :param db: the db connection
    :return: the id of the added social account

    Throws HTTP 422 Unprocessable Content if social media account is invalid
    """
    # VALIDATE THE SOCIAL ACCOUNT
    validate_social_account(social_account)

    # SAVE THE PHOTO ON THE FILESYSTEM, THEN PASS TO REPO THE FILE_PATH OF THE PROFILE PHOTO
    photo_path = save_profile_photo(social_account.profile_photo)

    social_acc_created = add_social_account(social_account.username,
                                            social_account.profile_description,
                                            social_account.no_followers,
                                            social_account.no_following,
                                            social_account.no_of_posts,
                                            photo_path,
                                            user_id, db)
    #TODO: PENTRU WEBSOCKET UPDATE CU PROFILUL CREAT
    return social_acc_created.id
