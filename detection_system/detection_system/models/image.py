from enum import Enum
from datetime import datetime
from typing import List, Optional

import numpy as np
from pydantic import Field

from .base import Base
from .annotation import BBOX


class ColorOrder(str, Enum):
    RGB = "rgb"
    BGR = "bgr"


class Image(Base):
    image: np.ndarray
    color_order: ColorOrder


class Frame(Image):
    time_created: datetime = Field(default_factory=datetime.now)


class AnnotatedFrame(Frame):
    objects: List[BBOX] = []

    def draw_objects(self, names: Optional[List[str]] = None) -> np.ndarray:
        frame = self.image.copy()

        for obj in self.objects:
            if not names or obj.obj_name in names:
                frame = BBOX.plot_object(frame, obj)
        return frame
