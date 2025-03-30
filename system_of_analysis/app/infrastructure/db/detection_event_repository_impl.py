from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from system_of_analysis.app.domain.models.detection_event import DetectionEventEntity
from system_of_analysis.app.domain.models.person_detection import PersonDetectionEntity, ViolationType
from system_of_analysis.app.domain.ports.detection_event_repo import DetectionEventRepository
from system_of_analysis.app.infrastructure.db import models


class DetectionEventRepositoryImpl(DetectionEventRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_event(self, event: DetectionEventEntity) -> DetectionEventEntity:
        timestamp_ms = int(event.timestamp.timestamp() * 1000)

        db_event = models.DetectionEvent(
            camera_id=event.camera_id,
            timestamp=timestamp_ms,
            image_url=event.image_url,
        )
        self.db.add(db_event)
        self.db.flush()

        for p in event.persons:
            person = models.PersonDetection(
                detection_event_id=db_event.id,
                violation=p.violation.value,
                bbox_x=p.bbox_x,
                bbox_y=p.bbox_y,
                bbox_width=p.bbox_width,
                bbox_height=p.bbox_height
            )
            self.db.add(person)

        self.db.commit()
        self.db.refresh(db_event)

        return DetectionEventEntity(
            id=db_event.id,
            camera_id=db_event.camera_id,
            timestamp=datetime.fromtimestamp(db_event.timestamp / 1000),
            image_url=db_event.image_url,
            persons=event.persons
        )

    def list_events(self) -> List[DetectionEventEntity]:
        """
        Возвращает все DetectionEvent из БД (без фильтров).
        """
        db_events = self.db.query(models.DetectionEvent).all()

        result = []
        for e in db_events:
            person_entities = [
                PersonDetectionEntity(
                    id=p.id,
                    violation=ViolationType(p.violation),
                    bbox_x=p.bbox_x,
                    bbox_y=p.bbox_y,
                    bbox_width=p.bbox_width,
                    bbox_height=p.bbox_height
                )
                for p in e.person_detections
            ]
            raw_ts = e.timestamp
            if isinstance(raw_ts, str):
                try:
                    raw_ts_dt = datetime.strptime(raw_ts, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # fallback на ISO, если вдруг так
                    raw_ts_dt = datetime.fromisoformat(raw_ts)
                timestamp_ = raw_ts_dt
            # Если это уже datetime — всё ок
            elif isinstance(raw_ts, datetime):
                timestamp_ = raw_ts
            # Если число (int/float) — переводим из миллисекунд
            else:
                timestamp = datetime.fromtimestamp(raw_ts / 1000)
            result.append(
                DetectionEventEntity(
                    id=e.id,
                    camera_id=e.camera_id,
                    timestamp=timestamp_,
                    image_url=e.image_url,
                    persons=person_entities
                )
            )
        return result

    def get_by_id(self, event_id: int) -> Optional[DetectionEventEntity]:
        db_event = self.db.query(models.DetectionEvent).filter_by(id=event_id).first()
        if not db_event:
            return None

        person_entities = [
            PersonDetectionEntity(
                id=p.id,
                violation=ViolationType(p.violation),
                bbox_x=p.bbox_x,
                bbox_y=p.bbox_y,
                bbox_width=p.bbox_width,
                bbox_height=p.bbox_height,
            )
            for p in db_event.person_detections
        ]
        return DetectionEventEntity(
            id=db_event.id,
            camera_id=db_event.camera_id,
            timestamp=datetime.fromtimestamp(db_event.timestamp / 1000),
            image_url=db_event.image_url,
            persons=person_entities
        )

    def get_by_camera_and_range(
            self, camera_id: int, start: datetime, end: datetime
    ) -> List[DetectionEventEntity]:
        start_ts = int(start.timestamp() * 1000)
        end_ts = int(end.timestamp() * 1000)

        db_events = (
            self.db.query(models.DetectionEvent)
            .filter(models.DetectionEvent.camera_id == camera_id)
            .filter(models.DetectionEvent.timestamp >= start_ts)
            .filter(models.DetectionEvent.timestamp <= end_ts)
            .all()
        )

        result = []
        for e in db_events:
            person_entities = [
                PersonDetectionEntity(
                    id=p.id,
                    violation=ViolationType(p.violation),
                    bbox_x=p.bbox_x,
                    bbox_y=p.bbox_y,
                    bbox_width=p.bbox_width,
                    bbox_height=p.bbox_height,
                )
                for p in e.person_detections
            ]
            result.append(
                DetectionEventEntity(
                    id=e.id,
                    camera_id=e.camera_id,
                    timestamp=e.timestamp,
                    image_url=e.image_url,
                    persons=person_entities
                )
            )

        return result
