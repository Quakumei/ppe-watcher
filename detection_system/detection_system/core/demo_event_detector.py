import asyncio
from pathlib import Path
from typing import Generator, List, Tuple
import cv2
import numpy as np

from detection_system.ml.nms import batched_nms
from detection_system.ml.sort import Sort
from detection_system.models.violation_ppe import (
    PersonInfo,
    ViolationPPEEvent,
    ViolationType,
)

from ..models.annotation import BBOX
from ..models.image import AnnotatedFrame, Frame
from ..utils.settings import PPEConfig, settings, EventDetectorSettings
from ..messaging.message_sender import SimplePikaMessageSender
from ..models.event import Event
from ..utils.logging import logger
from ..ml.detectron_cfg import get_inference_predictor
from .event_detector import EventDetector
from .frame_provider import SimpleVideoFrameProvider


class SimpleVideoEventDetector(EventDetector):
    def __init__(
        self, video: str, settings: EventDetectorSettings = settings
    ):
        self.settings = settings
        self.message_sender = SimplePikaMessageSender(
            settings.pika_connection_string, settings.pika_routing_key
        )
        self.frame_provider = SimpleVideoFrameProvider(video)
        self.ppe_config: PPEConfig = self.settings.ppe_config
        self.ppe_predictor = get_inference_predictor(self.settings.ppe_config)
        self.interesting_names = [
            # 'Hardhat',
            "NO-Hardhat",
            "NO-Safety Vest",
            # 'Safety Vest',
            # 'Person',
        ]
        self.object_trackers = {
            # 'Hardhat': Sort(min_hits=24, max_age=24),
            "NO-Hardhat": Sort(min_hits=24 * 3, max_age=6),
            "NO-Safety Vest": Sort(min_hits=24 * 3, max_age=6),
            # 'Safety Vest': Sort(min_hits=24, max_age=24),
            # 'Person': Sort(min_hits=24, max_age=24),
        }
        self.triggered_tracks = set()

    async def _submit_event(self, event: Event) -> None:
        logger.info(f"Event: {event}")
        message = await event.to_message()
        await self.message_sender.send(message)

    @staticmethod
    def bbox_abs_to_rel(
        bbox_abs: Tuple[float, float, float, float], frame_wh: Tuple[int, int]
    ) -> Tuple[float, float, float, float]:
        return (
            bbox_abs[0] / frame_wh[0],
            bbox_abs[1] / frame_wh[1],
            bbox_abs[2] / frame_wh[0],
            bbox_abs[3] / frame_wh[1],
        )

    def _pred_detector(self, image: np.ndarray) -> List[BBOX]:
        pred = self.ppe_predictor(image)
        pred = pred["instances"].to("cpu")
        idx_keep = batched_nms(
            pred.pred_boxes.tensor, pred.scores, pred.pred_classes, 0.8
        ).tolist()

        pred_objects = []
        for i, p in enumerate(
            zip(
                pred.scores.tolist(),
                pred.pred_boxes.tensor.tolist(),
                pred.pred_classes.tolist(),
            )
        ):
            if i not in idx_keep:
                continue
            score, bbox_abs, class_id = p
            class_name = self.settings.ppe_config.classes.get(class_id, str(class_id))
            bbox_rel = self.bbox_abs_to_rel(bbox_abs, pred.image_size[::-1])
            obj = BBOX(obj_name=class_name, bbox=bbox_rel, score=score)
            pred_objects.append(obj)
        return pred_objects

    def annotate_image(self, frame: Frame) -> AnnotatedFrame:
        objects = self._pred_detector(frame.image)
        return AnnotatedFrame(objects=objects, **frame.model_dump())

    def _track_objects(self, objects: List[BBOX]) -> List[BBOX]:
        new_objects = []
        for object_name, tracker in self.object_trackers.items():
            relevant_objects = list(
                filter(lambda x: x.obj_name == object_name, objects)
            )
            relevant_objects = [(*x.bbox, x.score) for x in relevant_objects]
            if relevant_objects:
                relevant_bboxes = np.array(relevant_objects)
            else:
                relevant_bboxes = np.empty((0, 5))
            new_bboxes = tracker.update(relevant_bboxes)
            for new_bbox in new_bboxes:
                new_obj = BBOX(
                    obj_name=object_name,
                    bbox=new_bbox[:4],
                    score=1,
                    track_id=new_bbox[-1],
                )
                new_objects.append(new_obj)

        return new_objects

    def iter_annotated_stream(self) -> Generator[AnnotatedFrame, None, None]:
        for annotated_frame in map(
            self.annotate_image, self.frame_provider.iter_stream()
        ):
            # Update using trackers
            new_objects = self._track_objects(annotated_frame.objects)
            annotated_frame.objects = new_objects
            yield annotated_frame

    async def trigger_violation_events(self, annotated_frame: AnnotatedFrame) -> None:
        violation_names = ["NO-Hardhat", "NO-Safety Vest"]
        new_objects = annotated_frame.objects
        for new_violation in filter(
            lambda x: x.obj_name in violation_names, new_objects
        ):
            if new_violation.track_id not in self.triggered_tracks:
                self.triggered_tracks.add(new_violation.track_id)
                obj_name_to_violation_type = {
                    "NO-Hardhat": ViolationType.NO_HELMET,
                    "NO-Safety Vest": ViolationType.NO_VEST,
                }
                bbox_rel = new_violation.bbox  # xyxy
                bbox_xywh = (
                    bbox_rel[0],
                    bbox_rel[1],
                    bbox_rel[2] - bbox_rel[0],
                    bbox_rel[3] - bbox_rel[1],
                )
                event = ViolationPPEEvent(
                    cam_id=0,
                    persons=[
                        PersonInfo(
                            violation=obj_name_to_violation_type.get(
                                new_violation.obj_name
                            ),
                            bbox_xywh=bbox_xywh,
                        )
                    ],
                    image=annotated_frame,
                )
                await self._submit_event(event)

    async def run(self) -> None:
        for annotated_frame in self.iter_annotated_stream():
            preview_frame = annotated_frame.draw_objects(names=self.interesting_names)
            await self.trigger_violation_events(annotated_frame)
            cv2.imshow("PPE Demo", preview_frame)
            cv2.waitKey(1)
