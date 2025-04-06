from fastapi import APIRouter, HTTPException, Depends

from app.domain.services.usecases import get_application_service, ApplicationService
from app.presentation.api.mappers import map_camera_in_to_entity, map_camera_entity_to_out
from app.presentation.api.schemas.camera import CameraIn, CameraOut

router = APIRouter()


@router.post("/", response_model=CameraOut)
def create_camera(camera_in: CameraIn, app_service: ApplicationService = Depends(get_application_service)):
    # Преобразуем входную схему в доменную модель
    camera_entity = map_camera_in_to_entity(camera_in)
    # Вызываем use-case, который уже создан с единой сессией
    created_camera = app_service.create_camera_uc.execute(camera_entity)
    return map_camera_entity_to_out(created_camera)


@router.get("/", response_model=list[CameraOut])
def list_cameras(app_service: ApplicationService = Depends(get_application_service)):
    cameras = app_service.list_cameras_uc.execute()
    return [map_camera_entity_to_out(cam) for cam in cameras]


@router.get("/{camera_id}", response_model=CameraOut)
def get_camera(camera_id: int, app_service: ApplicationService = Depends(get_application_service)):
    # Здесь мы можем вызвать метод репозитория напрямую через use-case (если он есть) или добавить отдельный use-case
    camera = app_service.list_cameras_uc.execute()  # пример: ищем в списке
    for cam in camera:
        if cam.id == camera_id:
            return map_camera_entity_to_out(cam)
    raise HTTPException(status_code=404, detail="Camera not found")
