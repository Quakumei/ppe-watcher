from system_of_analysis.app.domain.models.detection_event import DetectionEventEntity
from system_of_analysis.app.domain.ports.detection_event_repo import DetectionEventRepository


class AddDetectionEventUseCase:
    def __init__(self, detection_event_repo: DetectionEventRepository):
        self.detection_event_repo = detection_event_repo

    def execute(self, event: DetectionEventEntity) -> DetectionEventEntity:
        return self.detection_event_repo.create_event(event)
