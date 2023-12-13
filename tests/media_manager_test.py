""" Test MediaManager class """
from api.services.media_manager import MediaManager


class TestMediaManager:
    """Test class for testing MediaManager functions"""

    def test_scan_media_dir(self):
        """test scan_media_dir"""
        media_manager = MediaManager()
        for dir, file, mimetype in media_manager.scan_media_files():
            assert dir is not None and dir is not ""
            assert file is not None and file is not ""
            assert mimetype.startswith(("image", "video"))
