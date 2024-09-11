from .node import Node
from .btState import BTState

class Sequence(Node):
    def __init__(self, children):
        self.children = children

    def tick(self,):
        for child in self.children:
            status = child.tick()
            if status == BTState.FAILURE:
                return BTState.FAILURE
        return BTState.SUCCESS