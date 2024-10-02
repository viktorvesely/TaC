from typing import Callable
from ...state import State

type ActionFunc = Callable[[int, State], ActionFunc]