""" Manages all the aspects of media management """

import asyncio
import mimetypes
import os
from prisma import Prisma

from api.helper.getenv import get_env


class MediaManager:
    """Manages all the aspects of media management"""

    def __init__(self, prisma: Prisma) -> None:
        self.prisma = prisma

    def scan_media_files(self, mount_path=None):
        """list all the directory and files inside"""
        if mount_path is None:
            mount_path = get_env("MEDIA_DIRECTORY_PATH", "/usr/data")
        for entry in os.walk(mount_path):
            (parent_dir, _, files) = entry
            for file in files:
                (mimeType, _) = mimetypes.guess_type(file)
                if mimeType != None and mimeType.startswith(("image", "video")):
                    yield (parent_dir, os.path.join(parent_dir, file), mimeType)

    async def is_new_media(self, filepath):
        """Check if media present in DB"""
        return await self.prisma.media.find_first(where={"path": filepath})


async def main():
    prisma = Prisma()
    await prisma.connect()
    media_manager = MediaManager(prisma)
    result = await media_manager.is_new_media("/hello")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
