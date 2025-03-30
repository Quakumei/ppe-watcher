from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ViolationType(str, Enum):
    NONE = "none"
    NO_HELMET = "no_helmet"
    NO_VEST = "no_vest"
    NO_HELMET_NO_VEST = "no_helmet_no_vest"


@dataclass
class PersonDetectionEntity:
    id: Optional[int]
    violation: ViolationType
    bbox_x: float
    bbox_y: float
    bbox_width: float
    bbox_height: float
