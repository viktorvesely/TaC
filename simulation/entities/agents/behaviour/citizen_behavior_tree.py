import py_trees
from .citizen_actions import CitizenActions
from .behavior_tree import BehaviorTree

class CitizenBehaviorTree(BehaviorTree):
    def create_behavior_tree(self):
        root = py_trees.composites.Sequence("Citizen Behavior")

        # Roaming
        roam_node = py_trees.behaviours.Running(name="Roaming")
        roam_node.action = CitizenActions.roaming(self.agent)

        root.add_child(roam_node)
        return py_trees.trees.BehaviourTree(root)
