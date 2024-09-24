from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from .events.event import Event
    from .window import Window
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
        
        self.world: World = None
        self.events: list[Event] = []
        self.window: Window | None = None

        self.n_agents: int = -1
        self.start_t: float = 0
        self.t: float = 0
        self.last_tick: float = 0

        self.dTick_target: float = 17
        self.dTick: float = 0

        self.timescale: float = 1

        self.camera: Camera = None

        self.keys_pressed: set = set()
        
        self.agent_position: np.ndarray = None
        self.agent_velocity: np.ndarray = None
        self.agent_angle: np.ndarray = None
        self.agent_coords: np.ndarray = None
        self.agents_in_vision: np.ndarray = None
        self.agent_colors: np.ndarray = None
        self.agent_speed: np.ndarray = None
