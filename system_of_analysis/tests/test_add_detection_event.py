import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from system_of_analysis.app.domain.services.add_detection_event import AddDetectionEventUseCase

from system_of_analysis.app.domain.models.detection_event import DetectionEventEntity
from system_of_analysis.app.domain.models.person_detection import PersonDetectionEntity, ViolationType
from system_of_analysis.app.infrastructure.db import models
from system_of_analysis.app.infrastructure.db.database import Base
from system_of_analysis.app.infrastructure.db.detection_event_repository_impl import DetectionEventRepositoryImpl

# Тестовая база (in-memory SQLite)
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_add_detection_event(db):
    # Arrange: добавим камеру
    camera = models.Camera(rtsp_url="rtsp://test", name="Test Camera")
    db.add(camera)
    db.commit()
    db.refresh(camera)

    repo = DetectionEventRepositoryImpl(db)
    use_case = AddDetectionEventUseCase(repo)

    # Create domain model
    person = PersonDetectionEntity(
        id=None,
        detection_event_id=0,  # будет игнорироваться
        violation=ViolationType.NO_HELMET,
        bbox_x=0.1, bbox_y=0.2, bbox_width=0.3, bbox_height=0.4
    )

    event = DetectionEventEntity(
        id=None,
        camera_id=camera.id,
        timestamp=1234567890,
        image_url="http://example.com/img.png",
        persons=[person]
    )

    # Act
    created = use_case.execute(event)

    # Assert
    assert created.id is not None
    assert created.camera_id == camera.id
    assert created.timestamp == 1234567890
    assert created.image_url == "http://example.com/img.png"
    assert len(created.persons) == 1
    assert created.persons[0].violation == ViolationType.NO_HELMET
