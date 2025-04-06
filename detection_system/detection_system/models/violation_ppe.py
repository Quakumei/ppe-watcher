from enum import Enum
from typing import List, Optional, Tuple
from datetime import datetime

import numpy as np
from pydantic import Field

from .message import Message
from .base import Base
from .image import Image
from .event import Event
from ..core.image_uploader import image_uploader
from ..utils.settings import settings
from ..utils.logging import logger

RelativeBBoxXYWH = Tuple[float, float, float, float]


class ViolationType(str, Enum):
    NONE = "none"
    NO_VEST = "no_vest"
    NO_HELMET = "no_helmet"
    NO_HELMET_NO_VEST = "no_helmet_no_vest"


class PersonViolationMessageSchema(Base):
    violation: ViolationType
    bbox_xywh: RelativeBBoxXYWH


class ViolationPPEMessageSchema(Base):
    cam_id: int
    timestamp: str
    image_url: str
    persons: List[PersonViolationMessageSchema]


class PersonInfo(Base):
    violation: ViolationType
    bbox_xywh: RelativeBBoxXYWH


class ViolationPPEEvent(Event):
    cam_id: int
    persons: List[PersonInfo]
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    image: Optional[Image] = None

    async def _upload_image(self, image: np.ndarray, tag: str) -> str:
        # Upload file to minio here
        url = await image_uploader._upload_image(image, tag)
        expected_url = (
            f"https://{settings.minio_endpoint}/{settings.minio_bucket}/{tag}"
        )
        logger.info(f"Uploaded image to {expected_url}")
        return expected_url

    async def to_message(self) -> Message:
        image_url = await self._upload_image(
            self.image.image, f"cam{self.cam_id}_ts{int(self.timestamp.timestamp())}.jpeg"
        )
        return Message(
            data=ViolationPPEMessageSchema(
                cam_id=self.cam_id,
                timestamp=self.timestamp.isoformat(timespec="seconds"),
                image_url=image_url,
                persons=[
                    PersonViolationMessageSchema(**person.model_dump())
                    for person in self.persons
                ],
            )
        )

    def __str__(self):
        return f"{self.__class__.__name__}(cam_id={self.cam_id}, persons={self.persons}, timestamp={self.timestamp})"
