""" Manages all the aspects of media management """

import os
import shutil
import arrow
import mimetypes
from prisma import Prisma
from typing import BinaryIO
from fastapi import UploadFile
from PIL import Image, ExifTags
import api.config.constants as config
from api.helper.base_service import BaseServiceClass

from api.helper.getenv import get_env


class MediaManager(BaseServiceClass):
    """Manages all the aspects of media management"""

    def __init__(self, prisma: Prisma) -> None:
        super().__init__(prisma)
        self.media_home = get_env("MEDIA_DIRECTORY_PATH", "/usr/data")
        self.mkdir(self.media_home)

    def mkdir(self, path: str):
        if not os.path.exists(path):
            os.makedirs(path)

    def scan_media_files(self, mount_path=None):
        """list all the directory and files inside"""
        mount_path = self.media_home if mount_path is None else mount_path
        for entry in os.walk(mount_path):
            (parent_dir, _, files) = entry
            for file in files:
                (mimeType, _) = mimetypes.guess_type(file)
                if mimeType != None and mimeType.startswith(("image", "video")):
                    yield (parent_dir, os.path.join(parent_dir, file), mimeType)

    async def is_new_media(self, filepath):
        """Check if media present in DB"""
        return await self.prisma.media.find_first(where={"path": filepath})

    def get_date_time(self, exif_data: dict):
        for key in ["DateTime", "DateTimeOriginal", "DateTimeDigitized"]:
            if key in exif_data.keys():
                return arrow.get(exif_data[key], "YYYY:MM:DD HH:mm:ss")
        return None

    def get_exif(self, file: BinaryIO):
        img_exif = Image.open(file).getexif()
        exif_dict = dict()
        if img_exif is not None:
            for key, val in img_exif.items():
                if key in ExifTags.TAGS:
                    exif_dict[ExifTags.TAGS[key]] = val
                else:
                    exif_dict[key] = val
        return exif_dict

    async def save_to_disk(self, dest_path: str, media_file: UploadFile):
        self.mkdir(dest_path)
        try:
            with open(os.path.join(dest_path, media_file.filename), "wb+") as new_file:
                shutil.copyfileobj(media_file.file, new_file)
        finally:
            media_file.file.close()

    async def upload_media(self, file: UploadFile):
        exif_data = self.get_exif(file.file)
        datetime = self.get_date_time(exif_data) or arrow.now()

        db = await super().db()
        ORGANISE_BY = await db.config.find_first(where={"key": config.ORGANISE_BY})
        target_media_dir = os.path.join(self.media_home, str(datetime.date().year))

        return {"filename": media_file.filename}
