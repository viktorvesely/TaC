from .node import Node
from .btState import BTState
class Selector(Node):
    def __init__(self, children):
        self.children = children

    def tick(self,):
        for child in self.children:
            status = child.tick()
            if status == BTState.SUCCESS:
                return BTState.SUCCESS
        return BTState.FAILURE