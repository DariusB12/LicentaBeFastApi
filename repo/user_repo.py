
from model.entities import User
from sqlalchemy.orm import Session


def get_user_by_username(username: str, db: Session):
    """
    Returns the user with the given username
    :param username: the user's username
    :param db: the database connection
    :return: the user with the given username if exists, otherwise None
    """
    return db.query(User).filter(User.username == username).first()


def create_user(user: User, db: Session):
    """
    Creates a new user in the database.
    :param user: the user object to create
    :param db: the database connection
    :return: none
    """
    db.add(user)
    db.commit()
    db.flush()


def delete_user(user: User, db: Session):
    """
    Deletes the user from the database.
    :param user: the user object to be deleted
    :param db: the database connection
    :return: none
    """
    db.delete(user)
    db.commit()
    db.flush()

