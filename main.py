from exceptions.custom_exceptions import CustomHTTPException
from model.user import User
from routers import auth_router
from security.jwt_token import verify_token
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse


app = FastAPI()

app.include_router(auth_router.router)


@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    """
    Custom exception handles so that I can raise my custom exception anywhere and this function will
    handle the errors sending a Json response with the error details
    :param request: the request which caused this error
    :param exc: the error raised
    :return: Json response with the error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "status_code": exc.status_code
        }
    )


@app.get("/protected-data")
def get_protected_data(user: User = Depends(verify_token)):
    # Acces doar pentru utilizatori autentificați
    return {"message": "Acces permis!", "user": user.username}
