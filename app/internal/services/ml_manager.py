"""Module for all the ML related stuff"""
import warnings
from uuid import uuid4

import cv2
from cv2.typing import MatLike
from insightface.app import FaceAnalysis

import prisma
from app.internal.config.constants import ML_MODEL_DIRECTORY_PATH
from app.internal.helper.base_service import BaseServiceClass
from app.internal.helper.getenv import env
from app.internal.schema.face import Face

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
                    Face(
                        path=image_path,
                        embedding=face.embedding.tolist(),
                        age=face.age,
                        bbox=bbox,
                    )
                )
        return filtered

    def run_inference(self, media_path: str) -> list[Face]:
        with warnings.catch_warnings():
            img = cv2.imread(media_path)  # pylint: disable=no-member
            faces = self.__face_analysis.get(img)
            filtered_result = self.filter_faces(img, faces, media_path)
            return filtered_result

    async def get_matching_face_vector(self, uid: str, face: Face):
        db = await self.db()
        vector = f"'{str(face.embedding)}'"
        result = await db.query_raw(
            f"""
                                    
            SELECT f.* FROM "Face" f
            inner JOIN "Media" m
                on f.media_id = m.id
            inner JOIN "User" u
                on u.id = m.owner_id
            where u.id = '{uid}'
            order by f.vector <-> {vector} LIMIT 1;

            """,
            model=prisma.models.Face,
        )
        return result[0] if len(result) > 0 else None

    async def _save_face_object(self, media_id: str, face: Face):
        db = await self.db()
        bbox = str(face.bbox)
        vector = str(face.embedding)
        uuid = uuid4()
        return await db.query_raw(
            f""" INSERT INTO "Face" (id, media_id, bbox, vector) 
                VALUES ('{uuid}', '{media_id}', ARRAY {bbox},'{vector}'); """
        )

    async def save_face_model(self, user_id: str, media_id: str, faces: list[Face]):
        for face in faces:
            match = await self.get_matching_face_vector(user_id, face)
            if match is not None:
                await self._save_face_object(media_id, face)
