from typing import List

from sqlalchemy.orm import Session
from starlette import status

from app_requests.accounts_requests.update_social_account_post_req import PostComment
from app_responses.user_responses.social_accounts_response import SocialAccount
from exceptions.custom_exceptions import CustomHTTPException
from logging_config import logger
from model.entities import Post, Comment, PostPhoto, User, SocialMediaAccount
from datetime import datetime


def add_social_account_post(description, no_likes, no_comments, date_posted, comments, photos, social_account_id,
                            user_id: int, db: Session):
    """
    Adds a new post into the database to the given social media id
    :param user_id: the id of the current user
    :param date_posted:  the date the post was posted
    :param no_comments: the number of comments
    :param no_likes: the number of likes
    :param social_account_id: the account id of the post
    :param photos: the photos of the post
    :param comments: the comments of the post
    :param description: the description of the post
    :param db: the database session
    :return: the created post

    THROWS
        -HTTP_422_UNPROCESSABLE_ENTITY IF THE DATE STRING COULD NOT BE PARSED
        -HTTP 400 BAD_REQUEST if trying to add post to a social account that doesn't exist
                                    or doesn't belong to the current user
    """
    # CONVERT STRING DATE TO DATE_TIME
    try:
        date_posted_dt = datetime.fromisoformat(date_posted)
    except ValueError:
        logger.error("datePosted must be in ISO format (e.g., '2024-05-26T14:30:00')")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="datePosted must be in ISO format (e.g., '2024-05-26T14:30:00')"
        )

    social_account = db.query(SocialMediaAccount).filter(SocialMediaAccount.id == social_account_id).first()
    if not social_account or social_account.user_id != user_id:
        logger.error("the account to add the post doesn't belong to the current user or doesn't exist")
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="the account to add the post doesn't belong to the current user or doesn't exist"
        )
    # SET THE MODIFIED ATTRIBUTE OF THE SOCIAL ACCOUNT TO TRUE
    social_account.modified = True

    # FIRST WE CREATE THE POST AND THEN THE COMMENTS AND PHOTOS
    new_post = Post(
        description=description,
        noLikes=no_likes,
        noComments=no_comments,
        datePosted=date_posted_dt,
        social_account_id=social_account_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # REFRESH SO THAT THE CREATED ID IN THE POST IS VISIBLE IN THE VARIABLE

    # CREATE THE COMMENTS
    for comment_content in comments:
        comment = Comment(content=comment_content, post_id=new_post.id)
        db.add(comment)

    # CREATE THE PHOTOS
    for photo_path in photos:
        photo = PostPhoto(post_photo_filename=photo_path, post_id=new_post.id)
        db.add(photo)

    db.commit()

    return new_post


def delete_social_account_post(post_id: int, user_id: int, db: Session):
    """
    Delete the post from the database
    :param user_id: the current user's id
    :param post_id: the id of the post to delete
    :param db: the db connection
    :return: a list with all the photo filenames of the post to be deleted from system
    Throws
        -HTTP_400_BAD_REQUEST if the id of the post doesn't exist or if the post doesn't belong to the current user
    """
    # VERIFY THE POST BELONGS TO THE GIVEN USER
    post = db.query(Post).join(SocialMediaAccount).join(User).filter(User.id == user_id, Post.id == post_id).first()

    if not post:
        logger.error("Post does not exist or it doesn't belong to the current user")
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Post does not exist or it doesn't belong to the current user"
        )

    # WE NEED TO MARK THE FIELD modified=True IN THE SOCIAL ACCOUNT OF THE DELETED POST
    social_account = post.social_account
    if social_account:
        social_account.modified = True

    filenames = []
    # Posts photos
    for photo in post.photos:
        if photo.post_photo_filename:
            filenames.append(photo.post_photo_filename)

    db.delete(post)
    db.commit()
    db.flush()

    return filenames


def update_social_account_post(post_id: int, description: str, no_likes: int, no_comments: int, date_posted: str,
                               comments, photos, user_id, db) -> (Post, List[str]):
    """
      Updates the post in the database
      :param user_id: the current user id
      :param post_id: the post id
      :param date_posted:  the date the post was posted
      :param no_comments: the number of comments
      :param no_likes: the number of likes
      :param photos: the photos of the post
      :param comments: the comments of the post
      :param description: the description of the post
      :param db: the database session
      :return: the updated post

      THROWS
        -HTTP_422_UNPROCESSABLE_ENTITY IF THE DATE STRING COULD NOT BE PARSED
        -HTTP 400 BAD_REQUEST if the post doesn't belong to the current user
                                if the post doesn't exist
                                if the date of the post could not be parsed
      """
    # CONVERT STRING DATE TO DATE_TIME
    try:
        date_posted_dt = datetime.fromisoformat(date_posted)
    except ValueError:
        logger.error("datePosted must be in ISO format (e.g., '2024-05-26T14:30:00')")
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="datePosted must be in ISO format (e.g., '2024-05-26T14:30:00')"
        )

    # FIRST WE FETCH THE POST FROM DB AND VERIFY THE POST BELONGS TO THE GIVEN USER
    post = db.query(Post).join(SocialMediaAccount).join(User).filter(User.id == user_id, Post.id == post_id).first()
    if not post:
        logger.error("Post does not exist or it doesn't belong to the current user")
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Post does not exist or it doesn't belong to the current user"
        )

    # UPDATE POST FIELDS
    post.description = description
    post.noLikes = no_likes
    post.noComments = no_comments
    post.datePosted = date_posted_dt

    # DELETE THE OLD COMMENTS
    for comment in post.comments:
        db.delete(comment)

    # ADD THE NEW COMMENTS
    for comment in comments:
        db.add(Comment(content=comment.comment, post_id=post_id))

    # RETRIEVE THE OLD PHOTO FILEPATHS FROM POST_PHOTOS BEFORE DELETING THEM FROM DATA BASE
    old_photos_filenames = []
    for photo in post.photos:
        old_photos_filenames.append(photo.post_photo_filename)
        # DELETE THE OLD POST PHOTOS
        db.delete(photo)

    # ADD THE NEW POST PHOTOS
    for photo in photos:
        db.add(PostPhoto(post_photo_filename=photo.photo_url, post_id=post_id))

    # MARK THE SOCIAL ACCOUNT AS MODIFIED
    db.query(SocialMediaAccount).filter(SocialMediaAccount.id == post.social_account_id).update(
        {'modified': True})

    db.commit()
    db.refresh(post)

    return post, old_photos_filenames
