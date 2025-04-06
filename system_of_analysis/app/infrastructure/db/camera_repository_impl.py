from typing import List, Optional

from sqlalchemy.orm import Session

from system_of_analysis.app.infrastructure.db.models import Camera
from system_of_analysis.app.domain.models.camera import CameraEntity  # или Pydantic-схема, как вариант


class CameraRepositoryImpl:
    def __init__(self, db: Session):
        self.db = db

    def create(self, camera: CameraEntity) -> CameraEntity:
        db_cam = Camera(
            name=camera.name,
            rtsp_url=camera.rtsp_url,
            location=camera.location,
            is_active=camera.is_active
        )
        self.db.add(db_cam)
        self.db.commit()
        self.db.refresh(db_cam)
        return CameraEntity(
            id=db_cam.id,
            name=db_cam.name,
            rtsp_url=db_cam.rtsp_url,
            location=db_cam.location,
            is_active=db_cam.is_active
        )

    def get_all(self) -> List[CameraEntity]:
        cams = self.db.query(Camera).all()
        return [
            CameraEntity(
                id=c.id,
                name=c.name,
                rtsp_url=c.rtsp_url,
                location=c.location,
                is_active=c.is_active
            ) for c in cams
        ]

    def get_by_id(self, camera_id: int) -> Optional[CameraEntity]:
        c = self.db.query(Camera).filter_by(id=camera_id).first()
        if not c:
            return None
        return CameraEntity(
            id=c.id,
            name=c.name,
            rtsp_url=c.rtsp_url,
            location=c.location,
            is_active=c.is_active
        )
