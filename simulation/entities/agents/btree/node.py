
from ..agent import Agent
class Node:
    # Base class for all nodes, ACTION, SELECTOR, SEQUENCE, CONDITION, DECORATOR
    def __init__(self):
        self.status = None
    def tick(self,agent: Agent):
        raise NotImplementedError("Must be implemented by subclass")