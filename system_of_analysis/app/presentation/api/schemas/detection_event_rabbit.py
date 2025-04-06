from pydantic import BaseModel
from typing import List

class PersonDetectionRabbit(BaseModel):
    violation: str
    bbox_xywh: List[float]  # [x, y, width, height]

class DetectionEventRabbit(BaseModel):
    cam_id: int
    timestamp: str
    image_url: str
    persons: List[PersonDetectionRabbit]
