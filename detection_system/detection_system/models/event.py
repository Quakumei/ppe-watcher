from abc import ABC, abstractmethod

from .base import Base


class Event(Base, ABC):
    @abstractmethod
    def to_message(self):
        ...
