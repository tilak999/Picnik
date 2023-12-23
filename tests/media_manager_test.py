""" Test MediaManager class """

from app.internal.services.media_manager import MediaManager
from prisma import Prisma


class TestMediaManager:
    """Test class for testing MediaManager functions"""

    def test_scan_media_dir(self):
        """test scan_media_dir"""
        media_manager = MediaManager(prisma=Prisma())
        for directory, file, mimetype in media_manager.scan_media_files():
            assert directory is not None and directory != ""
            assert file is not None and file != ""
            assert mimetype.startswith(("image", "video"))
