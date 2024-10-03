import os
from typing import Literal, Self, Type

import numpy as np
import pandas as pd
from pathlib import Path
import datetime
import random
import json
from dataclasses import asdict

from ..state import State
from ..utils import Utils

class Event:

    def __init__(
        self,
        state: State
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

class ChosenTargetEvent(Event):

    def __init__(self, state: State, thief_i: int, target_i: bool, motivation: float, distance: float, p_not_caught: float) -> None:
        super().__init__(state)

        self.p_not_caught = p_not_caught
        self.thief_i = thief_i
        self.target_i = target_i
        self.distance = distance
        self.motivation = motivation

    @classmethod
    def construct_dataframe(cls, events) -> pd.DataFrame:
        return super().construct_dataframe(events, "p_not_caught", "thief_i", "target_i", "distance", "motivation")
    
class TheftAborted(Event):

    def __init__(self, state: State, thief_i: int, motivation: float, distance: float, reason: Literal["time", "motivation", "turned"]) -> None:
        super().__init__(state)

        self.thief_i = thief_i
        self.distance = distance
        self.motivation = motivation
        self.reason = reason


    @classmethod
    def construct_dataframe(cls, events) -> pd.DataFrame:
        return super().construct_dataframe(events, "thief_i", "distance", "motivation", "reason")

class TheftEvent(Event):

    def __init__(self, state: State, caught: bool, thief_i: int, target_i: int, vision: float, cos_angle: float) -> None:
        super().__init__(state)

        self.caught = caught
        self.thief_i = thief_i
        self.target_i = target_i
        self.vision = vision
        self.cos_angle = cos_angle

    @classmethod
    def construct_dataframe(cls, events) -> pd.DataFrame:
        return super().construct_dataframe(events, "caught", "thief_i", "target_i", "vision", "cos_angle")

class MotivationEvent(Event):

    def __init__(self, state: State, current: float, delta: float, thief_i: float, reason: str) -> None:
        super().__init__(state)

        self.current = current
        self.delta = delta
        self.thief_i = thief_i
        self.reason = reason

    @classmethod
    def construct_dataframe(cls, events) -> pd.DataFrame:
        return super().construct_dataframe(events, "current", "delta", "thief_i", "reason")


class VisionEvent(Event):

    def __init__(self, state: State, vision: np.ndarray) -> None:
        super().__init__(state)

        self.vision = vision

    @classmethod
    def construct_dataframe(cls, events, *keys) -> pd.DataFrame:
        
        dfs = []

        for event in events:
            df = pd.DataFrame(event.vision)
            df["t"] = event.t
            dfs.append(df)

        return pd.concat(dfs, ignore_index=True)

class MovementEvent(Event):

    def __init__(self, state: State, agent_position: np.ndarray) -> None:
        super().__init__(state)

        self.agent_position = agent_position

    @classmethod
    def construct_dataframe(cls, events, *keys) -> pd.DataFrame:
        
        dfs = []

        for event in events:
            df = pd.DataFrame(event.agent_position).rename(columns={0: "x", 1: "y"})
            df["t"] = event.t
            dfs.append(df)

        return pd.concat(dfs, ignore_index=True)
    
class MapEvent(Event):

    def __init__(self, state: State, walls: np.ndarray) -> None:
        super().__init__(state)

        self.walls = walls

    @classmethod
    def construct_dataframe(cls, events, *keys) -> pd.DataFrame:
        
        if len(events) > 1:
            raise ValueError("Only one map event is permitted")
    
        
        return pd.DataFrame(events[0].walls)
    

class EventManager:

    def __init__(self, state: State) -> None:
        self.monitoring = False
        self.events: dict[Type[Event], list[Event]] = dict()
        self.folder: Path | None = None
        self.state = state

    def add_event(self, event: Event):

        if not self.monitoring:
            return 
        
        events = self.events.get(event.__class__, [])
        events.append(event)
        self.events[event.__class__] = events

    def __enter__(self) -> Self:

        self.monitoring = True
        rand_id = random.randint(10_000, 100_000 - 1)
        now = datetime.datetime.now()
        self.folder = Utils.experiments_path() / self.state.vars.experiment_name / f"{now.strftime('%Y-%m-%d_%H-%M-%S')}_{rand_id}"
        self.folder.mkdir(parents=True)

        return self
    
    def __exit__(self, *args, **kwargs):

        self.monitoring = False

        for EventClass, events in self.events.items():
            df = EventClass.construct_dataframe(events)
            df.to_parquet(self.folder / f"{EventClass.__name__}.parquet", index=False)

        with open(self.folder / "config.json", "w", encoding="utf-8") as f:
            json.dump(asdict(self.state.vars), f)
        