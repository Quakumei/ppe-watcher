from abc import ABC, abstractmethod
import asyncio
from typing import Callable

from ..utils.settings import settings, Settings
from ..messaging.message_sender import PikaMessageSender
from ..models.violation_ppe import PersonInfo, ViolationPPEEvent, ViolationType
from ..models.event import Event
from ..utils.logging import logger


class AsyncRunnable(ABC):
    @abstractmethod
    async def run(self) -> None:
        pass

class EventDetector(AsyncRunnable):
    def __init__(self):
        pass

    async def run(self) -> None:
        raise NotImplementedError()

class FakeEventDetector(AsyncRunnable):
    """
        Sends a fake event every "period" seconds
    """
    def __init__(self,  fake_event_factory: Callable = lambda: ViolationPPEEvent(cam_id=0, persons=[PersonInfo(violation=ViolationType.NO_HELMET, bbox_xywh=(0.53, 0.44, 0.04, 0.06))]), period: int = 60, settings: Settings = settings):
        self.period = period
        self.fake_event_factory = fake_event_factory
        self.settings = settings
        self.message_sender = PikaMessageSender(settings.pika_connection_string, settings.pika_routing_key)
        asyncio.create_task(self.message_sender.start())

    async def _submit_event(self, event: Event) -> None:
        logger.info(f"Event: {event}")
        message = await event.to_message()
        logger.info(f"Send message: {message}")
        await self.message_sender.send(message)

    async def run(self) -> None:
        while True:
            await self._submit_event(self.fake_event_factory())
            await asyncio.sleep(self.period)
