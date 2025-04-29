from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator

import cv2

from ..models.image import ColorOrder, Frame


class VideoCapture(cv2.VideoCapture):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.release()


class AbstractFrameProvider(ABC):
    @abstractmethod
    def iter_stream(self) -> Generator[Frame, None, None]:
        ...


class SimpleVideoFrameProvider(AbstractFrameProvider):
    def __init__(self, video: str, loop: bool = True):
        self.video_path = video
        self.loop = loop

    def _provide_video_frames(self) -> Generator[Frame, None, None]:
        with VideoCapture(self.video_path) as cap:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = Frame(image=frame, color_order=ColorOrder.BGR)
                yield frame

    def iter_stream(self):
        while True:
            for frame in self._provide_video_frames():
                yield frame
            if not self.loop:
                break
