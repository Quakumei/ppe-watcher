from dataclasses import dataclass
from typing import Optional


@dataclass
class CameraEntity:
    id: Optional[int]
    name: Optional[str]
    rtsp_url: str
    location: Optional[str]
    is_active: bool = True
