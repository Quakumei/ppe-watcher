from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from app.domain.services.usecases import get_application_service, ApplicationService
from app.presentation.api.mappers import map_detection_event_in_to_entity, map_detection_event_entity_to_out
from app.presentation.api.schemas.detection_event import DetectionEventIn, DetectionEventOut

router = APIRouter()


@router.post("/", response_model=DetectionEventOut)
def add_detection_event(event_in: DetectionEventIn, app_service: ApplicationService = Depends(get_application_service)):
    event_entity = map_detection_event_in_to_entity(event_in)
    created_event = app_service.add_detection_event_uc.execute(event_entity)
    return map_detection_event_entity_to_out(created_event)


@router.get("/", response_model=list[DetectionEventOut])
def list_detection_events(
        camera_id: int | None = None,
        start: str | None = None,
        end: str | None = None,
        app_service: ApplicationService = Depends(get_application_service)
):
    events = app_service.list_detection_events_uc.execute(camera_id=camera_id, start=start, end=end)
    return [map_detection_event_entity_to_out(ev) for ev in events]


@router.get("/{event_id}", response_model=DetectionEventOut)
def get_detection_event(event_id: int, app_service: ApplicationService = Depends(get_application_service)):
    # Для получения одного события можно добавить отдельный use-case или вызывать репозиторный метод через ApplicationService
    # Предположим, что в репозитории есть get_by_id
    event = app_service.add_detection_event_uc.detection_event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return map_detection_event_entity_to_out(event)


@router.get("/export/datumaro", response_class=FileResponse)
def export_datumaro_format(
    camera_id: int | None = None,
    start: str | None = None,
    end: str | None = None,
    app_service: ApplicationService = Depends(get_application_service)
):
    print(f"camera_id={camera_id}, start={start}, end={end}")
    return app_service.export_datumaro_uc.execute(camera_id=camera_id, start=start, end=end)