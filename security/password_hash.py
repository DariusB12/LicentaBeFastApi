import bcrypt


def hash_password(password: str) -> str:
    """
    Creates a hash of the given password
    :param password: the password to be hashed
    :return: the hash of the password
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if the raw password and its hash matches
    :param plain_password: the plain password
    :param hashed_password: the hashed password
    :return: true if the password matches the hashed password, otherwise false
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

