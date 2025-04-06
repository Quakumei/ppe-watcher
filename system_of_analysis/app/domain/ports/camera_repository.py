from abc import ABC, abstractmethod
from typing import List, Optional

from system_of_analysis.app.domain.models.camera import CameraEntity


class CameraRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[CameraEntity]:
        pass

    @abstractmethod
    def get_by_id(self, camera_id: int) -> Optional[CameraEntity]:
        pass

    @abstractmethod
    def create(self, camera: CameraEntity) -> CameraEntity:
        pass

    @abstractmethod
    def delete(self, camera_id: int) -> None:
        pass

