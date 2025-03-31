from enum import Enum
from typing import List, Optional, Tuple
from datetime import datetime

from pydantic import AwareDatetime, Field

from .message import Message
from .base import Base
from .image import Image
from .event import Event

RelativeBBoxXYWH = Tuple[float,float,float,float]

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
    timestamp: int
    image_url: str
    persons: List[PersonViolationMessageSchema]

class PersonInfo(Base):
    violation: ViolationType
    bbox_xywh: RelativeBBoxXYWH

class ViolationPPEEvent(Event):
    cam_id: int
    persons: List[PersonInfo]
    timestamp: AwareDatetime = Field(default_factory=lambda: int(datetime.now().timestamp()))
    image: Optional[Image] = None

    async def to_message(self) -> Message:
        return Message(data=ViolationPPEMessageSchema(
            cam_id=self.cam_id,
            timestamp=self.timestamp,
            image_url="", # TODO: implement uploading of the image to the remote
            persons=[PersonViolationMessageSchema(**person.model_dump()) for person in self.persons]
        ))