from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from app.dependencies.oauth import LoggedInUser, verify_oauth
from app.internal.services.location_service import LocationService
from app.internal.services.media_manager import MediaManager
from app.internal.services.ml_manager import MlManager
from prisma import Prisma

router = APIRouter(
    prefix="/media", tags=["media"], dependencies=[Depends(verify_oauth)]
)
prisma = Prisma()

geo = LocationService()
mediaManager = MediaManager(prisma, location_service=geo)
mlManager = MlManager(prisma)


@router.post("/upload")
async def create_upload_file(
    media_file: UploadFile, user: Annotated[LoggedInUser, Depends(verify_oauth)]
):
    media_details = await mediaManager.upload_media(media_file, user)
    media = await mediaManager.save_metadata(media_details)
    thumbnail_path = await mediaManager.generate_thumbnail(media.id, media.path)

    faces = mlManager.run_inference(media.path)
    print(faces)

    return thumbnail_path
