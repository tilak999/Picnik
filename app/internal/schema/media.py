from typing import Any

from pydantic import BaseModel, Field

from app.dependencies.oauth import LoggedInUser


class MediaDetails(BaseModel):
    exif: dict
    media_file_name: str = Field(min_length=1)
    media_size: int
    media_path: str
    location: dict | Any
    mime_type: str
    user: LoggedInUser
