from sqlalchemy.orm import Session
from starlette import status

from exceptions.custom_exceptions import CustomHTTPException
from model.entities import Post, Comment, PostPhoto
from datetime import datetime


def add_social_account_post(description, no_likes, no_comments, date_posted, comments, photos, social_account_id,
                            db: Session):
    """
    Adds a new post into the database to the given social media id
    :param date_posted:  the date the post was posted
    :param no_comments: the number of comments
    :param no_likes: the number of likes
    :param social_account_id: the account id of the post
    :param photos: the photos of the post
    :param comments: the comments of the post
    :param description: the description of the post
    :param db: the database session
    :return: the created post

    THROWS HTTP_422_UNPROCESSABLE_ENTITY IF THE DATE STRING COULD NOT BE PARSED
    """
    # CONVERT STRING DATE TO DATE_TIME
    try:
        date_posted_dt = datetime.fromisoformat(date_posted)
    except ValueError:
        raise CustomHTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="datePosted must be in ISO format (e.g., '2024-05-26T14:30:00')"
        )

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
        photo = PostPhoto(post_photo_path=photo_path, post_id=new_post.id)
        db.add(photo)

    db.commit()

    return new_post
