from abc import ABC
from pydantic import BaseModel, ConfigDict

class Base(BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)
