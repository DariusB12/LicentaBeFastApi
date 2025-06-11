from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app_requests.auth_requests.login_request import LoginRequest
from app_requests.auth_requests.signup_request import SignUpRequest
from app_responses.auth_responses.auth_response import AuthResponse
from fastapi import Depends

from logging_config import logger
from model.entities import User
from security.jwt_token import verify_token

from database_connection.database import get_db
from service.auth_service import login, signup, delete
from websocket.websocket_connection import notify_client
from websocket.ws_types import WebsocketType

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login_api(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Login the user based on the provided credentials
    :param db: injecting the database dependency
    :param body: the body of the request
    :return: HTTP 200 OK if login is successful or HTTP 400 BAD_REQUEST otherwise
    """
    logger.info('Logging in')

    token = login(body.username, body.password, db)
    response = AuthResponse(
        message="Login successful",
        status_code=200,
        token=token
    )

    return JSONResponse(status_code=200, content=response.dict())


@router.post("/signup")
async def signup_api(body: SignUpRequest, db: Session = Depends(get_db)):
    """
    Signup the user based on the provided credentials
    :param db: injecting the database dependency
    :param body: the body of the request
    :return: 200 OK HTTPResponse or throws:
    - HTTP 409 Conflict if an account already exists with the provided username
    - HTTP 422 Unprocessable Content if the credentials are invalid
    """

    logger.info('Signing up')

    signup(body.username, body.password, db)
    response = AuthResponse(
        message="User registered successfully",
        status_code=200
    )

    return JSONResponse(status_code=200, content=response.dict())


@router.delete("/delete")
async def delete_api(body: LoginRequest, db: Session = Depends(get_db), user: User = Depends(verify_token)):
    """
    Deletes the user based on the provided credentials
    :param db: injecting the database dependency
    :param body: the body of the request
    :return: HTTP 200OK or throws:
    - HTTP 400 BAD_REQUEST if the credentials are not valid or if the user doesn't exist
    - HTTP 403 FORBIDDEN if the user token is invalid/expired (user must be logged in, in order to delete his account)
    """
    logger.info('Deleting user')

    user_id = delete(body.username, body.password, db)
    # NOTIFY WITH WS THE OTHER DISPOSITIVE THAT THIS ACCOUNT HAS BEEN DELETED
    await notify_client(user_id, None, WebsocketType.USER_ACCOUNT_DELETED)

    response = AuthResponse(
        message="User Account Deleted successfully",
        status_code=200
    )

    return JSONResponse(status_code=200, content=response.dict())
