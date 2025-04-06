from typing import Optional, Tuple
import numpy as np
from pydantic import BaseModel

from detection_system.core.plot import bbox_rel_to_abs, plot_bbox, plot_text_lines

OBJ_TO_COLOR_RGB = {}


class BBOX(BaseModel):
    obj_name: str
    bbox: Tuple[float, float, float, float]  # x1,y1,x2,y2 relative
    score: Optional[float] = None
    track_id: Optional[int] = None

    @staticmethod
    def plot_object(frame: np.ndarray, obj: "BBOX") -> np.ndarray:
        bbox_rel = obj.bbox
        bbox_abs = bbox_rel_to_abs(bbox_rel, frame.shape[:2][::-1])
        color_bgr = OBJ_TO_COLOR_RGB.get(obj.obj_name, (255, 255, 255))
        frame = plot_bbox(frame, bbox_abs, color_bgr, 1)
        annotation = ""
        if obj.score:
            annotation += f"{obj.score:.2f}"
        annotation += f"{obj.obj_name}"
        if obj.track_id:
            annotation += f" ({obj.track_id})"
        frame = plot_text_lines(
            frame, [annotation], p_abs=bbox_abs[:2], color=(255, 255, 255)
        )
        return frame
