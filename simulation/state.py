from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .events.event import Event
    from .window import Window
    from .world import world

from .utils import ms

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class State(metaclass=Singleton):

    def __init__(self) -> None:
        
        self.world: world 
        self.events: list[Event] = []
        self.window: Window | None = None

        self.t: int = 0
        self.last_draw: int = 0
        self.last_tick: int = 0

        self.dTick_target: int = ms(17)
        self.dTick: int = 0
        self.dDraw: int = 0

        self.timescale: float = 1
