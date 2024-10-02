import numpy as np
import random

from .agent_actions import ActionFunc
from ...state import State

introvert_roaming = 0
extrovert_roaming = 1
roaming_types = (introvert_roaming, extrovert_roaming)
roaming_weights = np.array([6, 1])
roaming_weights = roaming_weights / roaming_weights.sum()

class CitizenActions:
    
    weigths = np.array([15, 15, 1])
    weigths = weigths / weigths.sum()
    
    @staticmethod
    def select_action(i_agent: int, state: State):
        return np.random.choice(
            [CitizenActions.start_roaming, CitizenActions.select_poi, CitizenActions.social_interaction],
            p=CitizenActions.weigths  # 50% of roaming randomly, 40% move at POI, 10% engage in social interaction
        )

    
    @staticmethod
    def select_poi(i_agent: int, state: State):
        to = state.world.pois.select_random()
        state.maps.navigate_agent(i_agent, to, heuristic=state.maps.heuristic_avoid_dense)
        return CitizenActions.navigate
    
    @staticmethod
    def navigate(i_agent: int, state: State):

        if state.maps.execute_path(i_agent):
            return CitizenActions.wait_and_look(
                i_agent,
                state,
                random.randint(5_000, 15_000),
                np.pi / 6, CitizenActions.select_action
            )
        
    
        return CitizenActions.navigate
    

    @staticmethod
    def start_roaming(i_agent: int, state: State):

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
    def roaming(i_agent: int, state: State):
        if state.maps.execute_path(i_agent):
            return CitizenActions.wait_and_look(i_agent, state, 5_000, np.pi / 5, CitizenActions.select_action)
        return CitizenActions.roaming

  
    @staticmethod
    def wait_and_look(i_agent: int, state: State, time_ms: float, look_deviation: float, after_action: ActionFunc):

        t_finish = state.t + time_ms
        original_angle = state.agent_angle[i_agent]
        next_devation = state.t

        original_speed = state.agent_speed[i_agent, 0]
        state.agent_speed[i_agent] = 0

        def action(i_agent: int, state: State):
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
    def social_interaction(i_agent: int, state: State):

        agents_inds = state.grid.get_agents_around_cell(state.agent_coords[i_agent, :])
        engagement_probability = 0.3

        if agents_inds.size < 2:
            return CitizenActions.wait_and_look(i_agent, state, 3_000, random.random() * (np.pi / 4), CitizenActions.select_action)


        citizens_mask = state.agent_is_citizen[agents_inds.tolist()]

        interaction_mask = np.random.choice(
            [True, False],
            p=[engagement_probability, 1 - engagement_probability],
            size = agents_inds.size
        )

        interact_inds = agents_inds[interaction_mask & citizens_mask]

        if interact_inds.size < 2:
            return CitizenActions.wait_and_look(i_agent, state, 3_000, random.random() * (np.pi / 4), CitizenActions.select_action)


        positions = state.agent_position[interact_inds.tolist(), :]
        center = np.mean(positions, axis=0)
        deltas = center - positions
        angles = np.arctan2(deltas[:, 1], deltas[:, 0])

        for other_i, angle in zip(interact_inds, angles, strict=True):

            state.agent_angle[other_i] = angle
            state.world.agents.actions[other_i] = CitizenActions.wait_and_look(other_i, state, 10_000, 0, CitizenActions.select_action)

        return state.world.agents.actions[i_agent]