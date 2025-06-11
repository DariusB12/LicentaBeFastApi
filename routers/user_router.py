from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from fastapi import Depends

from app_responses.user_responses.social_accounts_response import SocialAccountsResponse
from logging_config import logger
from model.entities import User
from security.jwt_token import verify_token

from database_connection.database import get_db
from service.user_service import get_user_social_account

router = APIRouter(prefix="/user", tags=["UserAPI"])


@router.get("/accounts")
def social_accounts(user: User = Depends(verify_token), db: Session = Depends(get_db)):
    """
    Get all the social accounts of a user

    :param user: the user which is requesting the social accounts
    :param db: injecting the database dependency
    :return:
        -HTTP 200 OK if accounts retrieved successfully
        -HTTP 403 FORBIDDEN invalid token
        -HTTP 400 BAD_REQUEST if the user doesn't exist
    """
    logger.info("Get all user's social accounts")

    social_accounts_list = get_user_social_account(user.username, db)

    response = SocialAccountsResponse(
        message="Accounts retrieved successfully",
        status_code=200,
        social_accounts=social_accounts_list
    )

    return JSONResponse(status_code=200, content=response.dict())
