from typing import Optional
from pydantic import BaseModel, Field
from app.internal.helper.constants import MIN_STR_ID_LENGTH


class Device(BaseModel):
    id: str = Field(min_length=MIN_STR_ID_LENGTH)
    name: str
    user_id: Optional[str] = None
