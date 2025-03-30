from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from app.domain.models.person_detection import PersonDetectionEntity


@dataclass
class DetectionEventEntity:
    id: Optional[int]
    camera_id: int
    timestamp: int  # unix timestamp in ms
    image_url: str
    persons: List[PersonDetectionEntity]
