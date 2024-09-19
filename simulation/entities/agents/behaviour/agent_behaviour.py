import py_trees
from .agent_actions import AgentActions
from .behavior_tree import BehaviorTree

from functools import partial

class AgentBehaviour(BehaviorTree):
    

    def create_behavior_tree(self):
        root = py_trees.composites.Sequence("Agent Behaviour", True)

        condition = py_trees.composites.Selector("Condition", False)

        poi_sequence = py_trees.composites.Sequence("LOL", True)
        select_poi = py_trees.behaviours.Running(name="Select Poi")
        select_poi.action = partial(AgentActions.select_poi, self.i_agent)

        navigate = py_trees.behaviours.Running(name="Nav")
        navigate.action = partial(AgentActions.navigation, self.i_agent)
        poi_sequence.add_children([select_poi, navigate])

        roam_sequence = py_trees.composites.Sequence("roam", True)
        start_roam = py_trees.behaviours.Running(name="Start roam")
        start_roam.action = partial(AgentActions.start_roaming, self.i_agent)

        roaming = py_trees.behaviours.Running(name="Roaming")
        roaming.action = partial(AgentActions.roaming, self.i_agent)
        roam_sequence.add_children([start_roam, roaming])

        select_action = py_trees.behaviours.Running(name="axtoo")
        select_action.action = partial(AgentActions.select_action, self.i_agent)
        condition.add_children([select_action, poi_sequence])

        root.add_children([condition, roam_sequence])        
        return py_trees.trees.BehaviourTree(root)