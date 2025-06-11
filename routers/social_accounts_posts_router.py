from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from app_requests.accounts_requests.add_social_account_post_req import AddSocialAccountPostReq
from app_requests.accounts_requests.add_social_account_req import AddSocialAccountReq
from app_responses.social_accounts_responses.add_social_account_post_resp import AddSocialAccountPostResponse, \
    AddSocialAccountPostNotify, PostComment, PostPhoto
from app_responses.social_accounts_responses.add_social_account_resp import AddSocialAccountResponse
from app_responses.social_accounts_responses.delete_social_account_post_resp import DeleteSocialAccountPostResponse
from database_connection.database import get_db
from logging_config import logger
from security.jwt_token import verify_token
from service.social_accounts_posts_service import add_social_account_post_service, delete_social_account_post_service
from service.social_accounts_service import add_social_account_service
from sqlalchemy.orm import Session

from websocket.websocket_connection import notify_client
from websocket.ws_types import WebsocketType

router = APIRouter(prefix="/posts", tags=["postsApi"])


@router.post("/add")
async def add_new_social_account_post(body: AddSocialAccountPostReq, user=Depends(verify_token),
                                      db: Session = Depends(get_db)):
    """
    Adds the post of the given social account id to the database
    :param body: the request with the post
    :param user: for validating the token
    :param db: the db connection
    :return: HTTP 200OK if the post was created

    Throws HTTP 422 Unprocessable Content if the post is invalid
    Throws HTTP 403 FORBIDDEN if the user doesn't exist (invalid token)
    """
    logger.info('Adding new post')
    added_post = add_social_account_post_service(body, db)

    post_comments = []
    post_photos = []

    for comment in added_post.comments:
        post_comments.append(PostComment(
            id=comment.id,
            comment=comment.content
        ))

    for photo in added_post.photos:
        post_photos.append(PostPhoto(
            id=photo.id,
            photo_filename=photo.post_photo_filename
        ))

    notify_added_account = AddSocialAccountPostNotify(
        id=added_post.id,
        description=added_post.description,
        no_likes=added_post.noLikes,
        no_comments=added_post.noComments,
        date_posted=added_post.datePosted.isoformat(),

        comments=post_comments,
        photos=post_photos,
        profileId=added_post.social_account_id
    )

    response = AddSocialAccountPostResponse(
        message="Post added successfully",
        status_code=200,
    )

    # NOTIFY WITH WS THE OTHER DISPOSITIVE THAT THIS POST HAS BEEN ADDED
    await notify_client(user.id, notify_added_account.dict(), WebsocketType.POST_ADDED)

    return JSONResponse(status_code=200, content=response.dict())


@router.delete("/{post_id}")
async def delete_social_account_post_api(post_id: int, user=Depends(verify_token), db: Session = Depends(get_db)):
    """
    Deletes the post based on the given id
    :param post_id: the id of the post to be deleted
    :param user: for validating the token
    :param db: the db connection
    :return: HTTP 200OK if the post was deleted
    Throws
            -HTTP 400 BAD_REQUEST if the post doesn't belong to the current user or if the post doesn't exist
            -HTTP 403 FORBIDDEN if token is invalid
    """
    logger.info('Deleting post')
    delete_social_account_post_service(post_id, user.id, db)

    response = DeleteSocialAccountPostResponse(
        message="Post deleted successfully",
        status_code=200,
    )

    # NOTIFY WITH WS THE OTHER DISPOSITIVE THAT THIS SOCIAL ACCOUNT POST HAS BEEN DELETED
    await notify_client(user.id, post_id, WebsocketType.POST_DELETED)

    return JSONResponse(status_code=200, content=response.dict())


@router.put("/update")
async def update_new_social_account_post(body: AddSocialAccountPostReq, user=Depends(verify_token),
                                      db: Session = Depends(get_db)):
    """
    Adds the post of the given social account id to the database
    :param body: the request with the post
    :param user: for validating the token
    :param db: the db connection
    :return: HTTP 200OK if the post was created

    Throws HTTP 422 Unprocessable Content if the post is invalid
    Throws HTTP 403 FORBIDDEN if the user doesn't exist (invalid token)
    """
    #TODO: FUNCTIE DE UPDATE SOCIAL ACCOUNT, CAND SE FACE NOTIFY CU WEBSOCKET PE FRONTEND MODIFIED = TRUE
    logger.info('Adding new post')
    added_post = add_social_account_post_service(body, db)

    post_comments = []
    post_photos = []

    for comment in added_post.comments:
        post_comments.append(PostComment(
            id=comment.id,
            comment=comment.content
        ))

    for photo in added_post.photos:
        post_photos.append(PostPhoto(
            id=photo.id,
            photo_filename=photo.post_photo_filename
        ))

    notify_added_account = AddSocialAccountPostNotify(
        id=added_post.id,
        description=added_post.description,
        no_likes=added_post.noLikes,
        no_comments=added_post.noComments,
        date_posted=added_post.datePosted.isoformat(),

        comments=post_comments,
        photos=post_photos,
        profileId=added_post.social_account_id
    )

    response = AddSocialAccountPostResponse(
        message="Post added successfully",
        status_code=200,
    )

    # NOTIFY WITH WS THE OTHER DISPOSITIVE THAT THIS POST HAS BEEN ADDED
    await notify_client(user.id, notify_added_account.dict(), WebsocketType.POST_ADDED)

    return JSONResponse(status_code=200, content=response.dict())
