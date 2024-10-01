from typing import TYPE_CHECKING, Any, Type
from dataclasses import dataclass

import numpy as np

if TYPE_CHECKING:
    from .events.event import Event
    from .window import Window
    from .world.world import World
    from .camera import Camera
    from .world.navigation import GoogleMaps
    from .world.grid import Grid
    from .events.event import EventManager

@dataclass
class Vars: 

    experiment_name: str = "default"

    generation_lines_w: float = 30
    generation_corners_w: float = 10
    generation_cross_w: float = 10
    generation_empty_w: float = 25
    generation_one_w: float = 8
    
    n_thieves: int = 12
    n_citizens: int = 200
    agent_size: float = 10

    n_grids: int = 36
    
    

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class State(metaclass=Singleton):

    def __init__(self) -> None:
        
        self.world: World = None
        self.maps: GoogleMaps = None
        self.grid: Grid = None
        self.events: list[Event] = []
        self.window: Window | None = None
        self.event_manager: EventManager | None = None

        self.vars: Vars = Vars()

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
        self.agent_colors: np.ndarray = None
        self.agent_speed: np.ndarray = None
        self.agent_is_citizen: np.ndarray = None
        self.agent_motivations: np.ndarray = None
        self.agent_heading_vec: np.ndarray = None