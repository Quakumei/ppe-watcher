from pydantic import BaseModel

from .base import Base

class Message(Base):
    data: BaseModel

