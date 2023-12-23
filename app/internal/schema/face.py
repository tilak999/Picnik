from pydantic import BaseModel, Field


class Face(BaseModel):
    path: str = Field(min_length=1)
    embedding: list[float]
    age: float
    bbox: list[int]
