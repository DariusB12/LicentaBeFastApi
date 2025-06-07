import base64
import os
from uuid import uuid4


def save_profile_photo(base64_str) -> str:
    """
    Stores into the file system a photo received in base64 format
    :param base64_str: the photo to be stored
    :return: the file_path of the saved photo
    """
    # STRIP THE "data:image/png;base64," PREFIX IF PRESENT
    if base64_str.startswith('data:image'):
        base64_str = base64_str.split(',')[1]

    # DECODE THE IMAGE FROM BASE64
    img_data = base64.b64decode(base64_str)

    # PREPARE THE FILENAME AND FILE_PATHS TO THE SYSTEM DIRECTORY
    storage_dir = r"D:\UBB\Licenta\app\StoredPhotosDoNotDelete"
    filename = f"{uuid4().hex}.png"
    file_path = os.path.join(storage_dir, filename)

    # IF THE DIRECTORY DOESN'T EXIST THEN WE CREATE IT
    # Without exist_ok=True, trying to create a directory that already exists would raise a FileExistsError
    os.makedirs(storage_dir, exist_ok=True)

    # WRITE THE PHOTO TO THE FILE
    with open(file_path, "wb") as f:
        f.write(img_data)

    # RETURN THE FILE_PATH
    return file_path
