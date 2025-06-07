from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from app_requests.accounts_requests.add_social_account_post_req import AddSocialAccountPostReq
from app_requests.accounts_requests.add_social_account_req import AddSocialAccountReq
from app_responses.accounts_responses.add_social_accont_post_resp import AddSocialAccountPostResponse
from app_responses.accounts_responses.add_social_accont_resp import AddSocialAccountResponse
from database_connection.database import get_db
from security.jwt_token import verify_token
from service.social_accounts_posts_service import add_social_account_post_service
from service.social_accounts_service import add_social_account_service
from sqlalchemy.orm import Session

router = APIRouter(prefix="/posts", tags=["postsApi"])


@router.post("/add")
def add_new_social_account_post(body: AddSocialAccountPostReq, user=Depends(verify_token), db: Session = Depends(get_db)):
    """
    Adds the post of the given social account id to the database
    :param body: the request with the post
    :param user: for validating the token
    :param db: the db connection
    :return: HTTP 200OK if the post was created

    Throws HTTP 422 Unprocessable Content if the post is invalid
    Throws HTTP 403 FORBIDDEN if the user doesn't exist (invalid token)
    """
    add_social_account_post_service(body, db)

    response = AddSocialAccountPostResponse(
        message="Post added successfully",
        status_code=200,
    )

    return JSONResponse(status_code=200, content=response.dict())
