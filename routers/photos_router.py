from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
import os

from logging_config import logger
from security.jwt_token import verify_token
from model.entities import User


router = APIRouter(prefix="/photo", tags=["PhotosAPI"])

STORAGE_DIR = os.getenv("STORAGE_DIR")


@router.get("/{filename}")
def get_profile_photo(filename: str, user: User = Depends(verify_token)):
    """
    Searches the requested image filename on the system storage directory
    :param filename: the photo filename
    :param user: for token validation
    :return: FileResponse with the requested image
    """
    logger.info(f'Searching photo for filename: {filename}')
    full_path = os.path.join(STORAGE_DIR, filename)

    # VERIFY IF THE IMAGE EXISTS
    if not os.path.isfile(full_path):
        logger.error(f'image not found: {full_path}')
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(full_path, media_type="image/jpeg")
