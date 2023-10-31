""" Manages all the aspects of media management """

import mimetypes
import os


class MediaManager:
    """Manages all the aspects of media management"""

    def scan_media_files(self, mount_path=os.environ.get("KEY_THAT_MIGHT_EXIST")):
        """list all the directory and files inside"""
        mount_path = os.environ.get("KEY_THAT_MIGHT_EXIST")
        if mount_path is None:
            mount_path = "/mnt/onedrive/Pictures/Camera Roll/"
        for entry in os.walk(mount_path):
            (parent_dir, _, files) = entry
            for file in files:
                (mimeType, _) = mimetypes.guess_type(file)
                if mimeType != None and mimeType.startswith(("image", "video")):
                    yield (parent_dir, os.path.join(parent_dir, file), mimeType)


if __name__ == "__main__":
    media_manager = MediaManager()
    for dir, filepath, mimeType in media_manager.scan_media_files():
        print(dir, filepath, mimeType)
