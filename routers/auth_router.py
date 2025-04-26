from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api_responses.auth_response import AuthResponse
from api_requests.login_request import LoginRequest
from api_requests.signup_request import SignUpRequest
from fastapi import Depends

from database_connection.database import get_db
from service.auth_service import login, signup

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login_api(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Login the user based on the provided credentials
    :param db: injecting the database dependency
    :param body: the body of the request
    :return: HTTP 200 OK if login is successful or HTTP 400 BAD_REQUEST otherwise
    """
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
    :return: none or throws:
    - HTTP 409 Conflict if an account already exists with the provided username
    - HTTP 422 Unprocessable Content if the credentials are invalid
    """
    signup(body.username, body.password, db)

    response = AuthResponse(
        message="User registered successfully",
        status_code=200
    )

    return JSONResponse(status_code=200, content=response.dict())
