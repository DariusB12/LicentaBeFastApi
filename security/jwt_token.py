import os
from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC
from fastapi import Security, status
from exceptions.custom_exceptions import CustomHTTPException
from repo.user_repo import get_user_by_username
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from database_connection.database import get_db
from sqlalchemy.orm import Session

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


def create_access_token(data: dict):
    """
    Creates a JWT token for the given data, using an algorithm and a secret_key,
    and adds an expiration time to it
    :param data: the data to be stored in the JWT token
    :return: the token created
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


security = HTTPBearer()  # Defines the scheme for Bearer token


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Function used to validate the token received in a request
    :param db: the database connection
    :param credentials: HTTP authorization credentials
    :return: the corresponding user of the token if the token is valid, otherwise throws an HTTPException 403 Forbidden
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")
        if username is None:
            # If the token doesn't contain a username
            raise CustomHTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Token invalid"
            )

        user = get_user_by_username(username, db)
        if user is None:
            # If the username doesn't belong to anny registered account
            raise CustomHTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Token invalid"
            )
        return user
    except JWTError:
        # If the token is expired decode() function automatically throws JWTError
        raise CustomHTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            message="Token invalid"
        )
