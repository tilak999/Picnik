import os
import shutil
from fastapi import APIRouter, Depends, UploadFile
from prisma import Prisma
from api.dependency.OAuth2 import verifyOAuth
from api.helper.getenv import get_env
from api.services.auth_manager import AuthManager
from api.services.device_manager import DeviceManager
from api.services.user_manager import UserManager

router = APIRouter(prefix="/media", tags=["media"], dependencies=[Depends(verifyOAuth)])
prisma = Prisma()

deviceManager = DeviceManager(prisma)
userManager = UserManager(prisma)
authManager = AuthManager(userManager, deviceManager)


@router.post("/upload")
async def create_upload_file(media_file: UploadFile):
    dir_path = get_env("MEDIA_DIRECTORY_PATH")
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    try:
        with open(os.path.join(dir_path, media_file.filename), "wb+") as new_file:
            shutil.copyfileobj(media_file.file, new_file)
    finally:
        media_file.file.close()

    return {"filename": media_file.filename}
