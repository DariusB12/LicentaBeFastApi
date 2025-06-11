import base64
import os
from uuid import uuid4

STORAGE_DIR = os.getenv("STORAGE_DIR")


def save_profile_photo(base64_str) -> str:
    """
    Stores into the file system a photo received in base64 format
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
