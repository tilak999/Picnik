"""Module for all the ML related stuff"""
import warnings

import cv2
from cv2.typing import MatLike
from insightface.app import FaceAnalysis

from app.internal.config.constants import ML_MODEL_DIRECTORY_PATH
from app.internal.helper.base_service import BaseServiceClass
from app.internal.helper.getenv import env

warnings.filterwarnings("error")

providers = ["CPUExecutionProvider"]
provider_options = [{"arena_extend_strategy": "kSameAsRequested"}] * len(providers)


class MlManager(BaseServiceClass):
    """ML management service"""

    def __prepare_face_recog_model(self):
        self.__face_analysis = FaceAnalysis(
            name=self.__face_recog_model,
            root=self.__model_dir,
            providers=providers,
            provider_options=provider_options,
        )
        self.__face_analysis.prepare(ctx_id=0, det_size=(640, 640))

    def __init__(self, prisma) -> None:
        super().__init__(prisma=prisma, name=__name__)
        self.__model_dir = env("ML_MODEL_DIRECTORY_PATH", ML_MODEL_DIRECTORY_PATH)
        self.__face_recog_model = env("ML_MODEL_FACE_RECOGNITION", "buffalo_l")
        self.__prepare_face_recog_model()

    def expand_bbox(self, bbox: list[int], pt=10):
        """TODO: Need to improve logic to add boundry check"""
        [x1, y1, x2, y2] = bbox
        return [x1 - pt, y1 - pt, x2 + pt, y2 + pt]

    def calculate_area(self, bbox=None, width=0, height=0):
        if bbox is not None:
            [x1, y1, x2, y2] = bbox
            return (x2 - x1) * (y2 - y1)
        return width * height

    def filter_faces(self, image: MatLike, faces: list, image_path: str):
        filtered = []
        for face in faces:
            bbox = [int(point) for point in face["bbox"]]
            imgsize = [int(point) for point in image.shape]

            bbox_area = self.calculate_area(bbox)
            image_area = self.calculate_area(width=imgsize[0], height=imgsize[1])

            relative_area = (bbox_area / image_area) * 100
            if relative_area > 2:
                filtered.append(
                    {
                        "path": image_path,
                        "embedding": face.embedding,
                        "age": face.age,
                        "bbox": bbox,
                    }
                )
        return filtered

    def run_inference(self, media_path: str):
        img = cv2.imread(media_path)  # pylint: disable=no-member
        faces = self.__face_analysis.get(img)
        filtered_result = self.filter_faces(img, faces, media_path)
        return filtered_result
