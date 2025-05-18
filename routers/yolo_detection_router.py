from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from app_requests.yolo_requests.post_detection_request import PostDetectionRequest
from app_responses.yolo_responses.post_detection_response import PostDetectionResponse
from model.entities import User
from security.jwt_token import verify_token
from app_requests.yolo_requests.profile_detection_request import ProfileDetectionRequest
from app_responses.yolo_responses.profile_detection_response import ProfileDetectionResponse

from service.yolo_services.yolo_service import detect_from_profile_capture, detect_from_post_capture

router = APIRouter(prefix="/yolo", tags=["YoloAPI"])


@router.post("/profile")
def detect_profile_data(body: ProfileDetectionRequest, user: User = Depends(verify_token)):
    """
    If the data wasn't detected in the image then the following invalid input will be assigned to each label:
    profile_photo: None
    username = ''
    description = ''
    followers = -1
    following = -1
    posts = -1
    :param body: the body of the request containing the image in base64 format
    :param user: used as dependency for token validation
    :return: ProfileDetectionResponse containing all the data detected in the provided image, the profile photo
    will be sent in base64 format (because the user can change the photo in the frontend app if he wants)
    Throws 400 BAD_REQUEST if the image encoded in base64 doesn't represent a valid image
    """
    # print("image received:", body.image)
    profile_photo, username, description, followers, following, posts = detect_from_profile_capture(body.image)

    response = ProfileDetectionResponse(
        profile_photo=profile_photo,
        username=username,
        description=description,
        no_followers=followers,
        no_following=following,
        no_of_posts=posts,

        message="Profile data detected with success",
        status_code=200,
    )
    return JSONResponse(status_code=200, content=response.dict())


@router.post("/post")
def detect_post_data(body: PostDetectionRequest, user: User = Depends(verify_token)):
    """
    If the data wasn't detected in the image then the following invalid input will be assigned to each label:
    post_photo: None
    description = ''
    comments: []
    date = None
    no_likes = -1
    no_comments = -1

    The date format will be sent as string in the following format: "2025-03-12T00:00:00" ISO 8601 format
    (so on the frontend side I can easily convert it)

    :param body: the body of the request containing the image in base64 format
    :param user: used as dependency for token validation
    :return: PostDetectionResponse containing all the data detected in the provided image, the post photo
    will be sent in base64 format (because the user can change the photo in the frontend app if he wants)
    Throws 400 BAD_REQUEST if the image encoded in base64 doesn't represent a valid image
    """
    # print("image received:", body.image)
    post_photo, description, no_likes, no_comments, date,comments = detect_from_post_capture(body.image)

    response = PostDetectionResponse(
        post_photo=post_photo,
        description=description,
        no_likes=no_likes,
        no_comments=no_comments,
        date=date.isoformat() if date else None,
        comments=comments,

        message="Post data detected with success",
        status_code=200,
    )
    return JSONResponse(status_code=200, content=response.dict())
