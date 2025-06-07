from sqlalchemy.orm import Session

from model.entities import SocialMediaAccount


def add_social_account(username, profile_description, no_followers, no_following, no_of_posts, photo_path,
                       user_id: int, db: Session):
    """
    Adds a new social account into the database to the given user
    :param username: the username of the social account
    :param profile_description: the description of the social account
    :param no_followers: the no followers of the social account
    :param no_following: the no following of the social account
    :param no_of_posts: the no posts of the social account
    :param photo_path: the profile photo path of the social account
    :param user_id: the user id of the social account to be added
    :param db: the database session
    :return: the social media created account
    """

    new_account = SocialMediaAccount(
        user_id=user_id,
        username=username,
        profile_description=profile_description,
        no_followers=no_followers,
        no_following=no_following,
        no_of_posts=no_of_posts,
        profile_photo_path=photo_path
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)  # Ensures all DB-generated fields are available
    return new_account
