from abc import ABC, abstractmethod

from ..models.event import ViolationPPEEvent


class AbstractEventSubmitter(ABC):
    @abstractmethod
    def submit(event: ViolationPPEEvent) -> None:
        ...
