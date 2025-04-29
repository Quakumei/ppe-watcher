from typing import List, Tuple
import numpy as np
import cv2


def plot_point(
    frame: np.ndarray, p_abs: Tuple[int, int], color: Tuple[int, int, int], size: int
) -> np.ndarray:
    frame = cv2.circle(frame, p_abs, size, color, -1)
    return frame


def plot_line(
    frame: np.ndarray,
    p1: Tuple[int, int],
    p2: Tuple[int, int],
    color: Tuple[int, int, int],
    thickness: int = 3,
) -> np.ndarray:
    frame = cv2.line(frame, p1, p2, color, thickness=thickness)
    return frame


def plot_bbox(
    frame: np.ndarray,
    bbox_abs: Tuple[int, int, int, int],
    color: Tuple[int, int, int],
    thickness: int = 3,
):
    x1, y1, x2, y2 = bbox_abs
    frame = cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness=thickness)
    return frame


def plot_text_lines(
    frame: np.ndarray,
    text_lines: List[str],
    p_abs: Tuple[int, int],
    color: Tuple[int, int, int],
):
    x, y = p_abs
    text_writer_start = (x, y - 5)
    text_writer_step = (0, 20)
    # Draws lines from bottom to top
    for i, line in enumerate(text_lines[::-1]):
        frame = cv2.putText(
            frame,
            line,
            text_writer_start - np.int32(text_writer_step) * i,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2,
        )
    return frame


def bbox_abs_to_rel(
    bbox_abs: Tuple[float, float, float, float], frame_wh: Tuple[int, int]
) -> Tuple[float, float, float, float]:
    return (
        bbox_abs[0] / frame_wh[0],
        bbox_abs[1] / frame_wh[1],
        bbox_abs[2] / frame_wh[0],
        bbox_abs[3] / frame_wh[1],
    )


def bbox_rel_to_abs(
    bbox_rel: Tuple[float, float, float, float], frame_wh: Tuple[int, int]
) -> Tuple[float, float, float, float]:
    return tuple(
        map(
            int,
            (
                bbox_rel[0] * frame_wh[0],
                bbox_rel[1] * frame_wh[1],
                bbox_rel[2] * frame_wh[0],
                bbox_rel[3] * frame_wh[1],
            ),
        )
    )
