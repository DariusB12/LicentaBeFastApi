from exceptions.custom_exceptions import CustomHTTPException
from routers import auth_router, social_accounts_router, yolo_detection_router, translate_router, \
    social_accounts_posts_router, user_router, photos_router
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from websocket.websocket_connection import websocket_endpoint

app = FastAPI()
# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(auth_router.router)
app.include_router(social_accounts_router.router)
app.include_router(social_accounts_posts_router.router)
app.include_router(yolo_detection_router.router)
app.include_router(translate_router.router)
app.include_router(user_router.router)
app.include_router(photos_router.router)

app.add_api_websocket_route("/ws", websocket_endpoint)


@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    """
    Custom exception handler so that I can raise my custom exception anywhere and this function will
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


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Exception handler for any HTTPException that could be thrown in the app
    :param request: the request which caused this error
    :param exc: the error raised
    :return: Json response with the error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


