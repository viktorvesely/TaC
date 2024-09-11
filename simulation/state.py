from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from .events.event import Event
    from .test import GameWindow
    from .world.world import World
    from .camera import Camera

from .utils import ms

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class State(metaclass=Singleton):

    def __init__(self) -> None:
        
        self.agent_positions: np.ndarray = None

        self.world: World = None
        self.events: list[Event] = []
        self.window: GameWindow | None = None

        self.paused: bool = False
        self.t: int = 0
        self.last_tick: int = 0
        self.dTick_target: int = ms(17)
        self.dTick: int = 0

        self.timescale: float = 1

        self.camera: Camera = None

        self.keys_pressed: set = set()
        self.keys_pressing: set = set()

