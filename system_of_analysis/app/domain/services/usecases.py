from datetime import datetime
from typing import List, Optional

from fastapi import Depends

from app.domain.models.camera import CameraEntity
from app.domain.models.detection_event import DetectionEventEntity
from app.domain.ports.camera_repository import CameraRepository
from app.domain.ports.detection_event_repo import DetectionEventRepository
from app.infrastructure.db.camera_repository_impl import CameraRepositoryImpl
from app.infrastructure.db.database import get_db
from app.infrastructure.db.detection_event_repository_impl import DetectionEventRepositoryImpl


class ApplicationService:
    """
    Фабрика use-case‑ов, созданных с единой сессией БД.
    Этот класс инкапсулирует всю логику работы с БД для бизнес‑логики.
    """

    def __init__(self, db):
        self.db = db
        # Создаем репозитории на базе одной сессии
        camera_repo = CameraRepositoryImpl(db)
        detection_repo = DetectionEventRepositoryImpl(db)
        # Инициализируем use-case‑ы
        self.create_camera_uc = CreateCameraUseCase(camera_repo)
        self.list_cameras_uc = ListCamerasUseCase(camera_repo)
        self.add_detection_event_uc = AddDetectionEventUseCase(detection_repo)
        self.list_detection_events_uc = ListDetectionEventsUseCase(detection_repo)


def get_application_service(db=Depends(get_db)) -> ApplicationService:
    """
    Dependency для получения ApplicationService.
    Здесь сессия создается один раз на запрос и передается во все use-case‑ы.
    """
    return ApplicationService(db)


class CreateCameraUseCase:
    def __init__(self, camera_repo: CameraRepository):
        self.camera_repo = camera_repo

    def execute(self, camera: CameraEntity) -> CameraEntity:
        return self.camera_repo.create(camera)


class ListCamerasUseCase:
    def __init__(self, camera_repo: CameraRepository):
        self.camera_repo = camera_repo

    def execute(self) -> List[CameraEntity]:
        return self.camera_repo.get_all()


class AddDetectionEventUseCase:
    def __init__(self, detection_event_repo: DetectionEventRepository):
        self.detection_event_repo = detection_event_repo

    def execute(self, event: DetectionEventEntity) -> DetectionEventEntity:
        return self.detection_event_repo.create_event(event)


class ListDetectionEventsUseCase:
    def __init__(self, detection_event_repo: DetectionEventRepository):
        self.detection_event_repo = detection_event_repo

    def execute(self, camera_id: Optional[int] = None, start: Optional[str] = None, end: Optional[str] = None) -> List[
        DetectionEventEntity]:
        # Если заданы фильтры, используем get_by_camera_and_range
        if camera_id and start and end:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            return self.detection_event_repo.get_by_camera_and_range(camera_id, start_dt, end_dt)
        else:
            # Иначе возвращаем все события (предполагается, что репозиторий имеет list_events)
            return self.detection_event_repo.list_events()
