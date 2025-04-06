from abc import ABC, abstractmethod
import asyncio
from typing import Callable

from ..utils.settings import settings, EventDetectorSettings
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
