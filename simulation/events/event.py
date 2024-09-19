from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Event: # Base class for events, each with timestamp and type of event

    timestamp: datetime = field(init=False)
    name: str = field(init=False)

    def __post_init__(self):
        self.name = self.__class__.__name__ # Set event name to class name
        self.timestamp = datetime.now()     # Set timestamp to current time