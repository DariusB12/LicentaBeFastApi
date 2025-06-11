from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from app_requests.accounts_requests.add_social_account_req import AddSocialAccountReq
from app_requests.accounts_requests.update_social_account_req import UpdateSocialAccountReq
from app_responses.social_accounts_responses.add_social_account_resp import AddSocialAccountResponse
from app_responses.social_accounts_responses.delete_social_account_resp import DeleteSocialAccountResponse
from app_responses.social_accounts_responses.get_social_account_resp import GetSocialAccountResponse
from app_responses.social_accounts_responses.update_social_account_resp import UpdateSocialAccountResponse, \
    UpdateSocialAccountNotify
from app_responses.user_responses.social_accounts_response import SocialAccount
from database_connection.database import get_db
from logging_config import logger
from model.entities import User
from security.jwt_token import verify_token
from service.social_accounts_service import add_social_account_service, delete_social_account_service, \
    get_user_social_account_full_entity, update_social_account
from sqlalchemy.orm import Session

from websocket.websocket_connection import notify_client
from websocket.ws_types import WebsocketType

router = APIRouter(prefix="/accounts", tags=["socialAccountsApi"])


@router.post("/add")
async def add_new_social_account(body: AddSocialAccountReq, user=Depends(verify_token), db: Session = Depends(get_db)):
    """
    Adds the social media account to the current user
    :param body: the request with the social media account
    :param user: the current user (validating the token)
    :param db: the db connection
    :return: HTTP 200OK with the id of the created account

    Throws HTTP 422 Unprocessable Content if social media account is invalid
    Throws HTTP 403 FORBIDDEN if the user doesn't exist (invalid token)
    """
    logger.info("Adding new social media account")
    added_social_account = add_social_account_service(body, user.id, db)

    response = AddSocialAccountResponse(
        message="Social account added successfully",
        status_code=200,
        id=added_social_account.id
    )

    social_account_notify = SocialAccount(
        id=added_social_account.id,
        username=added_social_account.username,
        profile_photo_filename=added_social_account.profile_photo_filename,
        no_followers=added_social_account.no_followers,
        no_following=added_social_account.no_following,
        no_of_posts=added_social_account.no_of_posts,
        analysed=bool(added_social_account.analysis)
    )

    # NOTIFY WITH WS THE OTHER DISPOSITIVE THAT THIS SOCIAL ACCOUNT HAS BEEN DELETED
    await notify_client(user.id, social_account_notify.dict(), WebsocketType.PROFILE_ADDED)

    return JSONResponse(status_code=200, content=response.dict())


@router.delete("/delete/{social_account_id}")
async def delete_api(social_account_id: int, db: Session = Depends(get_db), user: User = Depends(verify_token)):
    """
    Deletes the social account based on the provided id
    :param social_account_id: the id of the social account to be deleted
    :param user: in order to validate the token
    :param db: injecting the database dependency
    :return: HTTP 200OK or throws:
    - HTTP 403 FORBIDDEN if invalid token
    - HTTP_400_BAD_REQUEST if the id of the social account doesn't exist or if it doesn't belong to the current user
    """
    logger.info(f'Deleting social account:{social_account_id}')

    delete_social_account_service(social_account_id,user.id, db)
    # NOTIFY WITH WS THE OTHER DISPOSITIVE THAT THIS SOCIAL ACCOUNT HAS BEEN DELETED
    await notify_client(user.id, social_account_id, WebsocketType.PROFILE_DELETED)

    response = DeleteSocialAccountResponse(
        message="Social Account Deleted successfully",
        status_code=200
    )

    return JSONResponse(status_code=200, content=response.dict())


@router.get("/{social_account_id}")
def social_account_by_id(social_account_id: int, user: User = Depends(verify_token), db: Session = Depends(get_db)):
    """
    Gets the social media account with the given id and returns it with all the components (posts and comments)

    :param social_account_id: the social media id
    :param user: the user which is requesting the social accounts
    :param db: injecting the database dependency
    :return:
        -HTTP 200 OK if account retrieved successfully
        -HTTP 403 FORBIDDEN invalid token
        -HTTP 400 BAD_REQUEST if the user doesn't exist
                                the social account doesn't exist
                                or the social account doesn't belong to the user
    """
    logger.info("Get user's social account, full entity")

    social_account = get_user_social_account_full_entity(social_account_id, user.username, db)

    response = GetSocialAccountResponse(
        message="Account retrieved successfully",
        status_code=200,
        social_account=social_account
    )

    return JSONResponse(status_code=200, content=response.dict())


@router.put("/update")
async def update_social_account_api(body: UpdateSocialAccountReq, user=Depends(verify_token),
                                    db: Session = Depends(get_db)):
    """
    Updates social media account
    :param body: the request with the social media account to be updated
    :param user: the current user (validating the token)
    :param db: the db connection
    :return: HTTP 200OK with the id of the created account
            - HTTP 400 BAD_REQUEST if social media account doesn't belong to the current user or if it doesn't exist
            - HTTP 422 Unprocessable Content if social media account is invalid
            - HTTP 403 FORBIDDEN if the user doesn't exist (invalid token)
    """
    logger.info(f"Update social media account,id={body.id}")
    updated_social_media_account = update_social_account(body, user.id, db)

    response = UpdateSocialAccountResponse(
        message="Social account updated successfully",
        status_code=200,
    )

    social_account_update_notify = UpdateSocialAccountNotify(
        id=updated_social_media_account.id,
        username=updated_social_media_account.username,
        profile_description=updated_social_media_account.profile_description,
        no_followers=updated_social_media_account.no_followers,
        no_following=updated_social_media_account.no_following,
        no_of_posts=updated_social_media_account.no_of_posts,
        profile_photo=updated_social_media_account.profile_photo_filename,
        modified=updated_social_media_account.modified
    )

    # NOTIFY WITH WS THE OTHER DISPOSITIVE THAT THIS SOCIAL ACCOUNT HAS BEEN DELETED
    await notify_client(user.id, social_account_update_notify.dict(), WebsocketType.PROFILE_EDITED)

    return JSONResponse(status_code=200, content=response.dict())
