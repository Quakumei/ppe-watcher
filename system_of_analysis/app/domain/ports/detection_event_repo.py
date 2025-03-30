from abc import ABC, abstractmethod
from typing import List, Optional
from system_of_analysis.app.domain.models.detection_event import DetectionEventEntity
from datetime import datetime


class DetectionEventRepository(ABC):
    @abstractmethod
    def create_event(self, event: DetectionEventEntity) -> DetectionEventEntity:
        pass

    @abstractmethod
    def get_by_camera_and_range(
        self, camera_id: int, start: datetime, end: datetime
    ) -> List[DetectionEventEntity]:
        pass

    @abstractmethod
    def get_by_id(self, event_id: int) -> Optional[DetectionEventEntity]:
        pass
