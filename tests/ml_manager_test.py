""" Test MlManager class """
import logging

import pytest

from app.internal.services.ml_manager import MlManager
from prisma import Prisma

logging.getLogger("prisma").setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_face_recognition():
    """test scan_media_dir"""
    ml_manager = MlManager(prisma=Prisma())
    faces = ml_manager.run_inference("/mnt/onedrive/picnik-data/test.jpg")
    await ml_manager._save_face_object("7dbae4ba-aee5-4441-8867-8f4e56f05982", faces[0])

    assert False
