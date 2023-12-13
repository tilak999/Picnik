""" Manages all the aspects of media management """

import datetime
import mimetypes
import os
import shutil
from uuid import uuid4

import arrow
from fastapi import UploadFile
from PIL import ExifTags, Image, TiffImagePlugin

import app.internal.config.constants as config
from app.dependencies.oauth import LoggedInUser
from app.internal.helper.base_service import BaseServiceClass
from app.internal.helper.exception import ServiceException
from app.internal.helper.getenv import env
from app.internal.schema.media import MediaDetails
from app.internal.services.location_service import LocationService
from prisma import Json, Prisma


class MediaManager(BaseServiceClass):
    """Manages all the aspects of media management"""

    def __init__(
        self, prisma: Prisma, location_service: LocationService | None = None
    ) -> None:
        super().__init__(prisma, name=__name__)
        self.media_home = env("MEDIA_DIRECTORY_PATH", "/usr/data")
        self.mkdir(self.media_home)
        self.location_service = location_service

    def mkdir(self, path: str):
        if not os.path.exists(path):
            os.makedirs(path)

    def get_mimetype(self, filename: str):
        (mime_type, _) = mimetypes.guess_type(filename)
        return mime_type

    def scan_media_files(self, mount_path=None):
        """list all the directory and files inside"""
        mount_path = self.media_home if mount_path is None else mount_path
        for entry in os.walk(mount_path):
            (parent_dir, _, files) = entry
            for file in files:
                mime_type = self.get_mimetype(file)
                if mime_type is not None and mime_type.startswith(("image", "video")):
                    yield (parent_dir, os.path.join(parent_dir, file), mime_type)

    async def is_new_media(self, filepath):
        """Check if media present in DB"""
        db = await self.db()
        return await db.media.find_first(where={"path": filepath})

    def get_date_time(self, exif_data: dict):
        for key in ["DateTime", "DateTimeOriginal", "DateTimeDigitized"]:
            if key in exif_data.keys():
                return arrow.get(exif_data[key], "YYYY:MM:DD HH:mm:ss")
        return None

    def format_exif_geotag(self, geotag: dict):
        geo_tags = {}
        for key, val in geotag.items():
            if key in ExifTags.GPSTAGS and type(val) not in [bytes]:
                tag = ExifTags.GPSTAGS[key]
                if type(val) in [tuple]:
                    geo_tags[tag] = tuple(map(float, val))
                else:
                    geo_tags[tag] = val
        return geo_tags

    def format_exif(self, img_exif: Image.Exif):
        exif_dict = {}
        if img_exif is not None:
            for key, val in img_exif.items():
                val = float(val) if type(val) in [TiffImagePlugin.IFDRational] else val
                if key in ExifTags.TAGS and type(val) not in [bytes]:
                    tag = ExifTags.TAGS[key]
                    if tag == "GPSInfo" and isinstance(val, dict):
                        exif_dict[tag] = self.format_exif_geotag(val)
                    else:
                        exif_dict[tag] = val
        return exif_dict

    async def get_target_directory(self, date: datetime.date):
        target_media_dir = os.path.join(self.media_home, str(date.year))
        organise_by = await super().get_config(config.ORGANISE_BY)
        if organise_by != "year":
            year = str(date.year)
            month = f"{date.month:02d}"
            target_media_dir = os.path.join(self.media_home, year, month)
        return target_media_dir

    async def check_if_exist(self, filepath: str):
        db = await self.db()
        return await db.media.find_first(where={"path": filepath})

    async def upload_media(self, media_file: UploadFile, user: LoggedInUser):
        uid = user.user_id
        file_name = media_file.filename or uuid4().hex[0:6]
        self.logger.info("Upload media: filename=%s, user=%s", file_name, uid)

        with Image.open(media_file.file) as media:
            exif_data = self.format_exif(media._getexif())  # type: ignore # pylint: disable=W0212
            address = {}
            if self.location_service is not None:
                address = await self.location_service.get_address(exif_data)

            media_time = self.get_date_time(exif_data) or arrow.now()
            target_media_dir = await self.get_target_directory(media_time.date())

            media_path = os.path.join(self.media_home, file_name)

            if await self.check_if_exist(media_path) is None:
                self.mkdir(target_media_dir)

                with open(media_path, "wb") as new_file:
                    media_file.file.seek(0)
                    shutil.copyfileobj(media_file.file, new_file)

                mime_type = Image.MIME[media.format] if media.format is not None else ""
                return MediaDetails(
                    exif=exif_data,
                    media_file_name=file_name,
                    media_size=media_file.size or 0,
                    media_path=media_path,
                    location=address,
                    mime_type=mime_type,
                    user=user,
                )
            raise ServiceException(
                name=self.get_name(),
                message=f"File already exist, filepath={media_path}",
            )

    async def get_media_by_id(self, media_id: str):
        db = await self.db()
        return db.media.find_first(where={"id": media_id})

    async def generate_thumbnail(self, media_id: str, filepath: str, size=(200, 200)):
        thumbnail_dir = os.path.join(self.media_home, ".thumbnails")
        thumb_file = os.path.join(thumbnail_dir, f"{media_id}.jpg")
        self.mkdir(thumbnail_dir)

        image = Image.open(filepath)
        if not image.mode == "RGB":
            image = image.convert("RGB")
        image.thumbnail(size)
        image.save(thumb_file, quality=85)
        return thumb_file

    async def save_metadata(self, media_details: MediaDetails):
        date = self.get_date_time(media_details.exif) or arrow.now()
        db = await self.db()
        result = await db.media.create(
            {
                "filename": media_details.media_file_name,
                "path": media_details.media_path,
                "filesize": media_details.media_size,
                "mimetype": media_details.mime_type,
                "originalDate": date.datetime,
                "location": Json(media_details.location),
                "rawExifData": Json(media_details.exif),
                "device_id": media_details.user.device_id,
                "owner_id": media_details.user.user_id,
            }
        )
        self.logger.debug(result)
        return result
