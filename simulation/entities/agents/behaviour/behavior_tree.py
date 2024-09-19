import py_trees
from .thief_actions import ThiefActions
from .citizen_actions import CitizenActions

class BehaviorTree:
    
    def __init__(self, i_agent: int):
        self.i_agent = i_agent
        self.tree = self.create_behavior_tree()
    
    def create_behavior_tree(self):
        raise NotImplementedError("Subclasses must implement this method")
    
    def tick(self):
        self.tree.tick()
        