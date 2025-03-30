from enum import Enum
from typing import List

from pydantic import BaseModel


class ViolationTypeEnum(str, Enum):
    none = "none"
    no_helmet = "no_helmet"
    no_vest = "no_vest"
    no_helmet_no_vest = "no_helmet_no_vest"


class PersonDetection(BaseModel):
    violation: ViolationTypeEnum
    bbox_x: float
    bbox_y: float
    bbox_width: float
    bbox_height: float


class DetectionEventIn(BaseModel):
    camera_id: int
    timestamp: str  # ISO-формат datetime, либо число, если договоримся о Unix-мсек
    image_url: str
    persons: List[PersonDetection]


class DetectionEventOut(DetectionEventIn):
    id: int
