import random
import numpy as np
from ...state import State

state = State()

class AgentActions:
    @staticmethod
    def select_poi(i_agent: int):
        state.world.maps.navigate_agent(i_agent)
        return AgentActions.navigation
    
    @staticmethod
    def navigation(i_agent: int):
        if state.world.maps.point(i_agent):
            return AgentActions.select_action
        
        return AgentActions.navigation

    @staticmethod
    def start_roaming(i_agent: int):
        return AgentActions.roaming()

    @staticmethod
    def roaming():

        finish_t = state.t + np.random.normal(loc=10_000, scale=1_000)
        multiplier = random.choice([-1, 1])

        def action(i_agent: int):
            
            if state.t >= finish_t:
                return AgentActions.select_action
            
            state.world.agents.look_random(i_agent, multiplier)
            
            return action
        
        return action


    @staticmethod
    def theft(i_agent: int):

        in_vision = state.agents_in_vision[i_agent, :]

        if in_vision[0] == -1:
            return AgentActions.start_roaming 

        state.agent_colors[i_agent, 0] = 0
        state.agent_colors[i_agent, 1] = 50
        state.agent_speed[i_agent, :] = 0.18
        target_i = np.random.choice(in_vision[in_vision != -1])
        
        def action(i_agent: int):
            
            delta = state.agent_position[target_i, :] - state.agent_position[i_agent, :]
            if np.linalg.norm(delta) < 8:
                state.agent_colors[i_agent, 0] = 255
                state.agent_colors[i_agent, 1] = 255
                state.agent_speed[i_agent, :] = 0.1
                return AgentActions.start_roaming
            
            angle = np.arctan2(delta[1], delta[0])
            state.agent_angle[i_agent] = angle

            return action

        return action
   
    weigths = np.array([3, 4, 1])
    weigths = weigths / weigths.sum()

    @staticmethod
    def select_action(i_agent: int):

        return np.random.choice(
            [AgentActions.select_poi, AgentActions.start_roaming, AgentActions.theft],
            p=AgentActions.weigths
        
        )
    