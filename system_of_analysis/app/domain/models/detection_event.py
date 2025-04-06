from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from system_of_analysis.app.domain.models.person_detection import PersonDetectionEntity


@dataclass
class DetectionEventEntity:
    id: Optional[int]
    camera_id: int
    timestamp: datetime
    image_url: str
    persons: List[PersonDetectionEntity]
