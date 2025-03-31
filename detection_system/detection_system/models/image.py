from enum import Enum
from datetime import datetime

import numpy as np
from pydantic import AwareDatetime, Field

from .base import Base

class ColorOrder(str, Enum):
    RGB = "rgb"
    BGR = "bgr"

class Image(Base):
    image: np.ndarray
    color_order: ColorOrder

class Frame(Image):
    time_received: AwareDatetime = Field(default_factory=datetime.now)