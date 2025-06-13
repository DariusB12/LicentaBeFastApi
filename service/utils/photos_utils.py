import base64
import os
from uuid import uuid4

from starlette import status

from exceptions.custom_exceptions import CustomHTTPException
from logging_config import logger

STORAGE_DIR = os.getenv("STORAGE_DIR")


def save_profile_photo(base64_str) -> str:
    """
    Stores into the file system a photo in png, which is received in base64 format
    :param base64_str: the photo to be stored
    :return: the filename of the saved photo
    """
    # STRIP THE "data:image/png;base64," PREFIX IF PRESENT
    if base64_str.startswith('data:image'):
        base64_str = base64_str.split(',')[1]

    # DECODE THE IMAGE FROM BASE64
    img_data = base64.b64decode(base64_str)

    # EACH IMAGE IS SAVED WITH A UNIQUE FILENAME
    # SAME IMAGE CAN BE SAVED MULTIPLE TIMES - eg IF LOADED BY MULTIPLE USERS
    filename = f"{uuid4().hex}.png"
    file_path = os.path.join(STORAGE_DIR, filename)

    # IF THE DIRECTORY DOESN'T EXIST THEN WE CREATE IT
    # Without exist_ok=True, trying to create a directory that already exists would raise a FileExistsError
    os.makedirs(STORAGE_DIR, exist_ok=True)

    # WRITE THE PHOTO TO THE FILE
    with open(file_path, "wb") as f:
        f.write(img_data)

    # RETURN THE FILENAME
    return filename


def get_photo_base64(filename: str) -> str:
    """
    Reads an image from the file system and returns it in base64 format.
    Assumes the image is a PNG.
    :param filename: the filename of the photo to be read
    :return: the base64 encoded string of the image
    Throws:
        -HTTP 400 BAD_REQUEST if the image is not found
                                or if an error occurred while reading
    """
    file_path = os.path.join(STORAGE_DIR, filename)

    if not os.path.exists(file_path):
        logger.error(f"Error: File '{file_path}' not found.")
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Error: File '{file_path}' not found."
        )

    try:
        with open(file_path, "rb") as f:
            img_data = f.read()
        # Encode the binary data to base64
        base64_str = base64.b64encode(img_data).decode('utf-8')
        # Add the data URI prefix (assuming PNG based on your save function)
        return base64_str
    except Exception as e:
        logger.error(f"Error reading or encoding file '{file_path}': {e}")
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Error reading or encoding file '{file_path}': {e}"
        )
