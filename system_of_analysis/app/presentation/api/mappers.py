from datetime import datetime

from app.domain.models.camera import CameraEntity
from app.domain.models.detection_event import DetectionEventEntity
from app.domain.models.person_detection import PersonDetectionEntity, ViolationType
from app.presentation.api.schemas.camera import CameraIn, CameraOut
from app.presentation.api.schemas.detection_event import DetectionEventIn, DetectionEventOut, PersonDetection


def map_camera_in_to_entity(camera_in: CameraIn) -> CameraEntity:
    return CameraEntity(
        id=None,
        name=camera_in.name,
        rtsp_url=camera_in.rtsp_url,
        location=camera_in.location,
        is_active=camera_in.is_active
    )


def map_camera_entity_to_out(camera: CameraEntity) -> CameraOut:
    return CameraOut(
        id=camera.id,
        name=camera.name,
        rtsp_url=camera.rtsp_url,
        location=camera.location,
        is_active=camera.is_active
    )


def map_detection_event_in_to_entity(event_in: DetectionEventIn) -> DetectionEventEntity:
    # Преобразуем timestamp в datetime (если он приходит как строка ISO)
    timestamp = datetime.fromisoformat(event_in.timestamp) if isinstance(event_in.timestamp,
                                                                         str) else datetime.fromtimestamp(
        event_in.timestamp / 1000)

    persons = [
        PersonDetectionEntity(
            id=None,
            violation=ViolationType(p.detection_event_id if hasattr(p, "detection_event_id") else p.violation.value),
            # Корректируем: берем значение из enum API
            bbox_x=p.bbox_x,
            bbox_y=p.bbox_y,
            bbox_width=p.bbox_width,
            bbox_height=p.bbox_height
        )
        for p in event_in.persons
    ]
    return DetectionEventEntity(
        id=None,
        camera_id=event_in.camera_id,
        timestamp=timestamp,
        image_url=event_in.image_url,
        persons=persons
    )


def map_detection_event_entity_to_out(event: DetectionEventEntity) -> DetectionEventOut:
    # Преобразуем timestamp обратно в ISO-формат
    if isinstance(event.timestamp, int):
        ts_dt = datetime.fromtimestamp(event.timestamp / 1000)
    else:
        ts_dt = event.timestamp

    ts_iso = ts_dt.isoformat()

    persons = [
        PersonDetection(
            violation=event_person.violation.value,
            bbox_x=event_person.bbox_x,
            bbox_y=event_person.bbox_y,
            bbox_width=event_person.bbox_width,
            bbox_height=event_person.bbox_height
        )
        for event_person in event.persons
    ]

    return DetectionEventOut(
        id=event.id,
        camera_id=event.camera_id,
        timestamp=ts_iso,
        image_url=event.image_url,
        persons=persons
    )

