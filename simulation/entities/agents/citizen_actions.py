import numpy as np
import random

from .agent_actions import ActionFunc
from ...state import State

state = State()

introvert_roaming = 0
extrovert_roaming = 1
roaming_types = (introvert_roaming, extrovert_roaming)
roaming_weights = np.array([4, 1])
roaming_weights = roaming_weights / roaming_weights.sum()

class CitizenActions:
    
    weigths = np.array([15, 15, 1])
    weigths = weigths / weigths.sum()
    
    @staticmethod
    def select_action(i_agent: int):
        return np.random.choice(
            [CitizenActions.start_roaming, CitizenActions.select_poi, CitizenActions.social_interaction],
            p=CitizenActions.weigths  # 50% of roaming randomly, 40% move at POI, 10% engage in social interaction
        )

    
    @staticmethod
    def select_poi(i_agent: int):
        to = state.world.pois.select_random()
        state.maps.navigate_agent(i_agent, to, heuristic=state.maps.heuristic_avoid_dense)
        return CitizenActions.navigate
    
    @staticmethod
    def navigate(i_agent: int):

        offset = np.random.random(2) * (state.grid.size / 2.2)

        def action(i_agent: int):
            if state.maps.execute_path(i_agent, offset):
                return CitizenActions.wait_and_look(
                    i_agent,
                    np.random.randint(5_000, 15_000),
                    np.pi / 6, CitizenActions.select_action
                )
            
            state.agent_velocity[i_agent, :] += np.random.random(2) * 0.06
            return action
    
        return action
    

    @staticmethod
    def start_roaming(i_agent: int):

        roaming_type = np.random.choice(roaming_types, p=roaming_weights)

        if roaming_type == introvert_roaming:
            walkable_density = state.grid.density[state.grid.walkable_mask].flatten().astype(float)
            walkable_density[walkable_density == 0.0] = 0.01
            walkable_density = 1 / walkable_density 
            walkable_inds = state.grid.grid_indicies[state.grid.walkable_mask].flatten()

            walkable_p = walkable_density / walkable_density.sum()
            go_to = np.random.choice(walkable_inds, p=walkable_p)
        
        elif roaming_type == extrovert_roaming:
            walkable_density = state.grid.density[state.grid.walkable_mask].flatten().astype(float)
            walkable_inds = state.grid.grid_indicies[state.grid.walkable_mask].flatten()

            walkable_p = walkable_density / walkable_density.sum()
            go_to = np.random.choice(walkable_inds, p=walkable_p)
            
        
        state.maps.navigate_agent(i_agent, go_to)

        return CitizenActions.roaming
    
    @staticmethod
    def roaming(i_agent: int):
        if state.maps.execute_path(i_agent):
            return CitizenActions.wait_and_look(i_agent, 5_000, np.pi / 5, CitizenActions.select_action)
        return CitizenActions.roaming

  
    @staticmethod
    def wait_and_look(i_agent: int, time_ms: float, look_deviation: float, after_action: ActionFunc):

        t_finish = state.t + time_ms
        original_angle = state.agent_angle[i_agent]
        next_devation = state.t

        original_speed = state.agent_speed[i_agent, 0]
        state.agent_speed[i_agent] = 0

        def action(i_agent: int):
            nonlocal next_devation
            
            if state.t >= t_finish:
                state.agent_speed[i_agent] = original_speed
                return after_action

            if state.t >= next_devation:
                state.agent_angle[i_agent] = original_angle + (random.random() - 0.5) * 2 * look_deviation
                next_devation += 800
        
            return action  

        return action


    @staticmethod
    def social_interaction(i_agent: int):

        agents_inds = state.grid.get_agents_around_cell(state.agent_coords[i_agent, :])
        engagement_probability = 0.3

        if agents_inds.size < 2:
            return CitizenActions.wait_and_look(i_agent, 3_000, random.random() * (np.pi / 4), CitizenActions.select_action)


        citizens_mask = state.agent_is_citizen[agents_inds.tolist()]

        interaction_mask = np.random.choice(
            [True, False],
            p=[engagement_probability, 1 - engagement_probability],
            size = agents_inds.size
        )

        interact_inds = agents_inds[interaction_mask & citizens_mask]

        if interact_inds.size < 2:
            return CitizenActions.wait_and_look(i_agent, 3_000, random.random() * (np.pi / 4), CitizenActions.select_action)


        positions = state.agent_position[interact_inds.tolist(), :]
        center = np.mean(positions, axis=0)
        deltas = center - positions
        angles = np.arctan2(deltas[:, 1], deltas[:, 0])

        for other_i, angle in zip(interact_inds, angles, strict=True):

            state.agent_angle[other_i] = angle
            state.world.agents.actions[other_i] = CitizenActions.wait_and_look(other_i, 10_000, 0, CitizenActions.select_action)

        return state.world.agents.actions[i_agent]

    @staticmethod
    def stop_at_citizen(i_agent: int, target_agent: int):
        """
        Makes the agent interact with a target agent (citizen), stopping movement once close.
        The agents look at each other, change color to yellow, and stop for a specified time.
        After the interaction, they resume moving away.
        """
        interaction_duration = 5_000  # 5 seconds in simulation time
        finish_t = state.t + interaction_duration

        # Both agents' colors change to yellow
        state.agent_colors[i_agent, :] = [255, 255, 0]  # Yellow
        state.agent_colors[target_agent, :] = [255, 255, 0]  # Yellow
        
        # Calculate the delta position between the two agents
        delta = state.agent_position[target_agent, :] - state.agent_position[i_agent, :]
        
        # If the agents are within 8 units of each other
        if np.linalg.norm(delta) < 8:
            # Make them look at each other
            angle = np.arctan2(delta[1], delta[0])
            state.agent_angle[i_agent] = angle
            state.agent_angle[target_agent] = angle + np.pi  # Opposite direction
            
            # Define the inner action that gets repeated during the interaction period
            def action(i_agent: int):
                # Stop both agents
                state.agent_speed[i_agent, :] = 0
                state.agent_speed[target_agent, :] = 0
                
                # Continue until the interaction time is over
                if state.t >= finish_t:
                    # After the interaction, both agents will move away
                    CitizenActions.move_away(i_agent)
                    CitizenActions.move_away(target_agent)
                    return CitizenActions.select_action  # Proceed to the next action after interaction
                
                # Keep returning the same action until the time is up
                return action
            
            return action

