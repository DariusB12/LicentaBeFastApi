from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from database_connection.database import get_db
from model.entities import User
from app_responses.user_response import UserResponse
from security.jwt_token import verify_token
from service.user_service import accounts_dto_list
from sqlalchemy.orm import Session

router = APIRouter(prefix="/user", tags=["UserApi"])


@router.get("/accounts")
def get_accounts_dto_list(user: User = Depends(verify_token), db: Session = Depends(get_db)):
    """
    Returns all the user's accounts in dtos
    :param user: the user whose accounts will be returned
    :param db: injecting the db connection
    :return: the list with all the accounts,
    or throws an CustomHTTPException 403 FORBIDDEN if the user doesn't exist (invalid token)
    """
    accounts = accounts_dto_list(user.username, db)
    response = UserResponse(
        message="Accounts retrieved successfully",
        accounts=accounts,
        status_code=200,
    )

    return JSONResponse(status_code=200, content=response.dict())


