from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from app_requests.accounts_requests.add_social_account_req import AddSocialAccountReq
from app_responses.accounts_responses.add_social_accont_resp import AddSocialAccountResponse
from database_connection.database import get_db
from security.jwt_token import verify_token
from service.social_accounts_service import add_social_account_service
from sqlalchemy.orm import Session

router = APIRouter(prefix="/accounts", tags=["socialAccountsApi"])


@router.post("/add")
def add_new_social_account(body: AddSocialAccountReq, user=Depends(verify_token), db: Session = Depends(get_db)):
    """
    Adds the social media account to the current user
    :param body: the request with the social media account
    :param user: the current user (validating the token)
    :param db: the db connection
    :return: HTTP 200OK with the id of the created account

    Throws HTTP 422 Unprocessable Content if social media account is invalid
    Throws HTTP 403 FORBIDDEN if the user doesn't exist (invalid token)
    """
    account_id = add_social_account_service(body, user.id, db)

    response = AddSocialAccountResponse(
        message="Social account added successfully",
        status_code=200,
        id=account_id
    )

    return JSONResponse(status_code=200, content=response.dict())
