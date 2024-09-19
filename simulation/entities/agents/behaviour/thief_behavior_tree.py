import py_trees
from .thief_actions import ThiefActions
from .behavior_tree import BehaviorTree

class ThiefBehaviorTree(BehaviorTree):
    
    def create_behavior_tree(self):
        root = py_trees.composites.Sequence("Thief Behavior")

        # Roaming
        roam_node = py_trees.behaviours.Running(name="Roaming")
        roam_node.action = ThiefActions.roaming(self.agent)

        # Target selection and closing distance
        target_selection = py_trees.composites.Sequence(name="Target Selection")
        select_target_node = py_trees.behaviours.Success(name="Select Target")
        select_target_node.action = ThiefActions.select_target(self.agent)
        close_distance_node = py_trees.behaviours.Success(name="Close Distance")
        close_distance_node.action = ThiefActions.close_distance(self.agent)
        scan_environment_node = py_trees.behaviours.Success(name="Scan Environment")
        scan_environment_node.action = ThiefActions.scan_environment(self.agent)
        target_selection.add_children([select_target_node, close_distance_node, scan_environment_node])

        # Decision to proceed with theft
        proceed_decision = py_trees.composites.Selector(name="Proceed with Theft?")
        proceed_yes_node = py_trees.behaviours.Success(name="Proceed")
        proceed_yes_node.action = ThiefActions.proceed_with_theft(self.agent)
        proceed_no_node = py_trees.behaviours.Failure(name="Abort and Return to Roaming")
        proceed_no_node.action = ThiefActions.abort_theft(self.agent)
        proceed_decision.add_children([proceed_yes_node, proceed_no_node])

        # Theft node
        theft_node = py_trees.behaviours.Success(name="Commit Theft")
        theft_node.action = ThiefActions.commit_theft(self.agent)

        # Theft success or failure
        theft_outcome = py_trees.composites.Selector(name="Theft Successful?")
        theft_success_node = py_trees.behaviours.Success(name="Theft Success")
        theft_success_node.action = ThiefActions.theft_success(self.agent)
        theft_fail_node = py_trees.behaviours.Failure(name="Theft Fail")
        theft_fail_node.action = ThiefActions.theft_fail(self.agent)
        theft_outcome.add_children([theft_success_node, theft_fail_node])

        root.add_children([roam_node, target_selection, proceed_decision, theft_node, theft_outcome])
        return py_trees.trees.BehaviourTree(root)