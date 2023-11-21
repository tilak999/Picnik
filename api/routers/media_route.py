from fastapi import APIRouter, Depends, UploadFile
from prisma import Prisma
from api.dependency.OAuth2 import verifyOAuth
from api.services.media_manager import MediaManager

router = APIRouter(prefix="/media", tags=["media"], dependencies=[Depends(verifyOAuth)])
prisma = Prisma()

mediaManager = MediaManager(prisma)


@router.post("/upload")
async def create_upload_file(media_file: UploadFile):
    exif = mediaManager.get_exif(media_file.file)
    d = mediaManager.get_date_time(exif) or 
    print(d.date().year)
