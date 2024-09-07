
from typing import Never

from .animation import Animation

class NoAnimation(Animation[Never]):
    def __init__(self):
        super().__init__(None)
        self.finished = True