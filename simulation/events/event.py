from typing import Self, Type

import numpy as np
import pandas as pd
from pathlib import Path
import datetime
import random

from ..state import State
from ..utils import Utils

state = State()


class Event:

    def __init__(
        self
    ) -> None:
        
        self.t = state.t
        state.event_manager.add_event(self)
    
    @classmethod
    def construct_dataframe(cls, events,  *keys) -> pd.DataFrame:
        df = dict()

        keys = list(keys) + ["t"]

        for event in events:
            for key in keys:
                col = df.get(key, [])
                col.append(getattr(event, key))
                df[key] = col
        
        return pd.DataFrame(df)

class TheftEvent(Event):

    def __init__(self, caught: bool, thieve_i: int, target_i: int, vision: float, cos_angle: float) -> None:
        super().__init__()

        self.caught = caught
        self.thieve_i = thieve_i
        self.target_i = target_i
        self.vision = vision
        self.cos_angle = cos_angle

    @classmethod
    def construct_dataframe(cls, events) -> pd.DataFrame:
        return super().construct_dataframe(events, "caught", "thieve_i", "target_i", "vision", "cos_angle")

class MovementEvent(Event):

    def __init__(self, agent_position: np.ndarray) -> None:
        super().__init__()

        self.agent_position = agent_position

    @classmethod
    def construct_dataframe(cls, events, *keys) -> pd.DataFrame:
        
        dfs = []

        for event in events:
            df = pd.DataFrame(event.agent_position).rename(columns={0: "x", 1: "y"})
            df["t"] = event.t
            dfs.append(df)

        return pd.concat(dfs, ignore_index=True)

class EventManager:

    def __init__(self) -> None:
        self.monitoring = False
        self.events: dict[Type[Event], list[Event]] = dict()
        self.folder: Path | None = None

    def add_event(self, event: Event):

        if not self.monitoring:
            return 
        
        events = self.events.get(event.__class__, [])
        events.append(event)
        self.events[event.__class__] = events

    def __enter__(self) -> Self:

        self.monitoring = True
        rand_id = random.randint(1_000, 10_000)
        now = datetime.datetime.now()
        self.folder = Utils.experiments_path() / f"{now.strftime('%Y-%m-%d_%H-%M-%S')}_{rand_id}"
        self.folder.mkdir(parents=True)

        return self
    
    def __exit__(self, *args, **kwargs):

        self.monitoring = False

        for EventClass, events in self.events.items():
            df = EventClass.construct_dataframe(events)
            df.to_parquet(self.folder / f"{EventClass.__name__}.parquet", index=False)
        