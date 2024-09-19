import numpy as np
from ....state import State

state = State()

class AgentActions:
    @staticmethod
    def select_poi(i_agent: int):
        print("sp")
        state.world.maps.navigate_agent(i_agent)
        return True
    
    @staticmethod
    def navigation(i_agent: int):
        print("n")
        return state.world.maps.point(i_agent)

    @staticmethod
    def start_roaming(i_agent: int):
        print("sr")
        state.world.agents.start_roaming(i_agent)
        return True

    @staticmethod
    def roaming(i_agent: int):
        print("r")
        return state.world.agents.roaming(i_agent)
   
    @staticmethod
    def select_action():
        print("")
        return np.random.random() > 0.5