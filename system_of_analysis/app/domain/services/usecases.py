from datetime import datetime
from typing import List, Optional
import json
import tempfile
import zipfile
import os
from fastapi import Depends
from fastapi.responses import FileResponse

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
        self.export_datumaro_uc = ExportDatumaroUseCase(detection_repo)


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


class ExportDatumaroUseCase:
    def __init__(self, detection_repo: DetectionEventRepository):
        self.detection_repo = detection_repo

    def execute(self, camera_id: Optional[int], start: Optional[str], end: Optional[str]) -> FileResponse:
        if camera_id and start and end:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            events = self.detection_repo.get_by_camera_and_range(camera_id, start_dt, end_dt)
        else:
            events = self.detection_repo.list_events()

        category_map = {
            "none": 0,
            "no_helmet": 1,
            "no_vest": 2,
            "no_helmet_no_vest": 3,
        }

        images, annotations = [], []
        ann_id = 1
        for i, event in enumerate(events):
            image_id = i + 1
            images.append({
                "id": image_id,
                "file_name": os.path.basename(event.image_url),
                "width": 1920,
                "height": 1080
            })
            for person in event.persons:
                annotations.append({
                    "id": ann_id,
                    "image_id": image_id,
                    "bbox": [
                        person.bbox_x * 1920,
                        person.bbox_y * 1080,
                        person.bbox_width * 1920,
                        person.bbox_height * 1080
                    ],
                    "category_id": category_map[person.violation.value],
                    "area": person.bbox_width * person.bbox_height * 1920 * 1080,
                    "iscrowd": 0
                })
                ann_id += 1

        temp_dir = tempfile.mkdtemp()
        ann_dir = os.path.join(temp_dir, "dataset", "annotations")
        img_dir = os.path.join(temp_dir, "dataset", "images")
        os.makedirs(ann_dir)
        os.makedirs(img_dir)

        with open(os.path.join(ann_dir, "instances_default.json"), "w", encoding="utf-8") as f:
            json.dump({
                "images": images,
                "annotations": annotations,
                "categories": [{"id": v, "name": k} for k, v in category_map.items()],
                "info": {}
            }, f, ensure_ascii=False, indent=2)

        with open(os.path.join(temp_dir, "dataset", "dataset_meta.json"), "w") as f:
            json.dump({"categories": list(category_map.keys())}, f)

        zip_path = os.path.join(temp_dir, "datumaro_export.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for folder, _, files in os.walk(os.path.join(temp_dir, "dataset")):
                for file in files:
                    full_path = os.path.join(folder, file)
                    arcname = os.path.relpath(full_path, temp_dir)
                    zipf.write(full_path, arcname)

        return FileResponse(zip_path, filename="datumaro_export.zip", media_type="application/zip")
