from typing import Optional

from pydantic import BaseModel


class CameraIn(BaseModel):
    name: Optional[str]
    rtsp_url: str
    location: Optional[str]
    is_active: bool = True


class CameraOut(CameraIn):
    id: int
