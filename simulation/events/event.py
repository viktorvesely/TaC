from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Event:

    timestamp: datetime = field(init=False)
    name: str = field(init=False)

    def __post_init__(self):
        self.name = self.__class__.__name__
        self.timestamp = datetime.now()