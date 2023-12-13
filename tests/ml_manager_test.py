""" Test MlManager class """
from api.services.ml_manager import MlManager


def test_face_recognition():
    """test scan_media_dir"""
    ml_manager = MlManager()
    faces = ml_manager.identify_faces("/workspaces/Picnik/test.jpg")
    print(faces)
    assert False
