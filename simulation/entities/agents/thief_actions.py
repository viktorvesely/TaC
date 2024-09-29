import random
import numpy as np
from ...state import State

state = State()

class ThiefActions():
    """
    Contains the actions of the thief agent.
    """

    @staticmethod
    def selects_dense_area(i_agent: int):
        walkable_density = state.grid.density[state.grid.walkable_mask].flatten()
        walkable_inds = state.grid.grid_indicies[state.grid.walkable_mask].flatten()

        walkable_p = walkable_density / walkable_density.sum()
        go_to = np.random.choice(walkable_inds, p=walkable_p)
        
        # Yuo can create your own heuristic function
        state.world.maps.navigate_agent(i_agent, go_to, heuristic=None)
        return ThiefActions.navigate
    
    @staticmethod
    def navigate(i_agent: int):
        # Check if the agent has reached the point of interest
        state.agent_colors[i_agent, :] = [255, 0, 0]  # Set color to red for "investigating"
        state.agent_motivations[i_agent]+= state.dTick / 10000  # Increase motivation over time

        if state.world.maps.execute_path(i_agent):
            # If the point of interest is reached, select the next point of interest
            return ThiefActions.selects_dense_area
        elif state.agent_motivations[i_agent] >= 0.5:
            return ThiefActions.look_for_target  # Start looking for a target
        # Continue navigating until the point of interest is reached
        return ThiefActions.navigate
    
    @staticmethod
    def look_for_target(i_agent: int):
        """
        If an appropriate target is found, start approaching.
        Otherwise, continue looking for a target.
        """
        agents_in_vision = state.agents_in_vision[i_agent, :]
        agent_mask = agents_in_vision != -1
        agent_in_vision_inds = agents_in_vision[agent_mask]
        
        # Check if there are any visible agents
        for target_i in agent_in_vision_inds:

            if not state.agent_is_citizen[target_i]:
                continue

            target_coords = state.agent_coords[target_i, :]
            factor1 = -state.world.vision.values[target_coords[0], target_coords[1]]
            factor2 = state.agent_motivations[i_agent]


            if (factor1 + factor2) > 0.5:
                return ThiefActions.approach_target(i_agent, target_i)  # Start approaching the selected target
            
        return ThiefActions.navigate  

    @staticmethod
    def approach_target(i_agent: int, target_i: int):
        """
        Approach the target. If close enough, attempt theft.
        """
        state.agent_speed[i_agent, :] = 0.18  # Increase speed while approaching
        #never goes in :(
        def action(i_agent: int):
            # Calculate distance to the target
            delta = state.agent_position[target_i, :] - state.agent_position[i_agent, :]
            # If within range, attempt theft
            # print(f"Thief {i_agent} approaching target {target_i} with distance {np.linalg.norm(delta)}")
            angle = np.arctan2(delta[1], delta[0])
            state.agent_angle[i_agent] = angle
            if np.linalg.norm(delta) < 28:
                state.agent_speed[i_agent, :] = 0.1
                return ThiefActions.theft(i_agent, target_i)
            return action  # Keep approaching if not close enough
        
        return action

    @staticmethod
    def theft(i_agent: int, target_i: int):
        """
        Attempt to steal from the target.
        """

        target_pos = state.agent_position[target_i]
        from_target_to_thief = state.agent_position[i_agent] - target_pos

        from_target_to_thief = from_target_to_thief / np.linalg.norm(from_target_to_thief)
        approach_cos_angle = np.dot(from_target_to_thief, state.agent_heading_vec[target_i])
        p_caught_by_target = approach_cos_angle / 2 + 0.5
        p_caught_by_target = min(p_caught_by_target, 0.95)

        thief_coords = state.agent_coords[i_agent, :]
        vision_value = state.world.vision.values[thief_coords[0], thief_coords[1]]
        p_caught_by_others = min(vision_value, 0.95)
        
        p_caught = max(p_caught_by_target, p_caught_by_others)
        
        caught = random.random() < p_caught
        print(caught, p_caught_by_target, p_caught_by_others)
        if caught:
            state.agent_motivations[i_agent] -= 0.2
        else:
            state.agent_motivations[i_agent] = 0

        return ThiefActions.selects_dense_area
    

