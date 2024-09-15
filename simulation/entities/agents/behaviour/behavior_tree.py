import py_trees
from .thief_actions import ThiefActions
from .citizen_actions import CitizenActions
from ...agent import Agent

class BehaviorTree:
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.tree = self.create_behavior_tree()
    
    def create_behavior_tree(self):
        raise NotImplementedError("Subclasses must implement this method")
    
    def update(self):
        self.tree.tick()
        