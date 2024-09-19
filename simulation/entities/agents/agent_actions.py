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

        finish_t = state.t + np.random.normal(loc=10, scale=2)

        def action(i_agent: int):
            
            if state.t >= finish_t:
                return AgentActions.select_action
            
            state.world.agents.look_random(i_agent)
            
            return action
        
        return action

    
   
    @staticmethod
    def select_action(i_agent: int):
        kek = np.random.random()
        if kek > 0.5:
            print("nav")
            return AgentActions.select_poi
        else:
            print("roam")
            return AgentActions.start_roaming