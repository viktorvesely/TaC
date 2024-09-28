import random
import numpy as np
from ...state import State

state = State()

class ThiefActions():
    """
    Contains the actions of the thief agent.
    """

    @staticmethod
    def select_point_of_interest(i_agent: int):
        # Start navigating to a point of interest
        
        state.world.maps.navigate_agent(i_agent)
        return ThiefActions.navigate
    
    @staticmethod
    def navigate(i_agent: int):
        # Check if the agent has reached the point of interest
        state.agent_speed[i_agent, :] = 0.1
        state.agent_colors[i_agent, :] = [255, 0, 0]  # Set color to red for "investigating"
        state.agent_motivations[i_agent]+= state.t /1000.0 # Increase motivation over time

        if state.world.maps.point(i_agent):
            # If the point of interest is reached, select the next point of interest
            return ThiefActions.select_point_of_interest(i_agent)
        elif state.agent_motivations[i_agent] >= 0.5:
            ThiefActions.look_for_target(i_agent)  # Start looking for a target
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
        agents = agents_in_vision[agent_mask]
        
        # Check if there are any visible agents
        agents_in_vision_coords = state.agent_coords[agents, :]
        for agent in agents_in_vision_coords:
            if (-state.world.vision.values[agent[0], agent[1]] + state.agent_motivations[i_agent]) > 0.5:
                return ThiefActions.approach_target(i_agent, agent)  # Start approaching the selected target
            
        return ThiefActions.look_for_target  

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
            print(f"Thief {i_agent} approaching target {target_i} with distance {np.linalg.norm(delta)}")
            if np.linalg.norm(delta) < 600:
                return ThiefActions.theft(i_agent, target_i)
            return action  # Keep approaching if not close enough
        
        return action

    @staticmethod
    def theft(i_agent: int, target_i: int):
        """
        Attempt to steal from the target.
        """
        print("Thief- Stealing from target")
        
        # 50% chance of successful theft in each case result should be stored, in state?
        success_chance = state.agent_motivations[i_agent] - random.random()
        if success_chance > 0.5:
            print(f"Thief {i_agent} successfully stole from {target_i}")
            state.agent_colors[i_agent, :] = [255, 255, 0]  
            state.agent_motivations[i_agent] = 0.0  # Reset motivation
        else:
            print(f"Thief {i_agent} failed to steal from {target_i}")
            state.agent_colors[i_agent, :] = [128, 128, 128]  
            state.agent_motivations[i_agent] -= 0.2  # Decrease motivation after failure

        return ThiefActions.select_point_of_interest(i_agent)
    

