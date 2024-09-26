import random
import numpy as np
from ...state import State

state = State()

class ThiefActions():
    """
        Return only functions not execute them
    """
    #This is similar to agent_actions.py 's roaming function
    @staticmethod
    def start_looking_for_target(i_agent: int):
        return ThiefActions.looking_for_target(i_agent)
     
    @staticmethod
    def start_approaching_target(i_agent: int):
        return ThiefActions.approach_target(i_agent)
    
    @staticmethod
    def looking_for_target(i_agent: int):
        """
           If appropiate target found, start aproaching to target calling ThiefActions.approach_target
           Else keep looking for target  
        """
        agents_in_vision = state.agents_in_vision[i_agent, :]
        agent_mask = agents_in_vision != -1
        agents = agents_in_vision[agent_mask]
        
        agents_in_vision_coords = state.agent_coords[agents, :]
        
        for agent in agents_in_vision_coords:
            if state.world.vision.values[agent[0], agent[1]] < 0:
                return ThiefActions.approach_target
            
        return ThiefActions.looking_for_target
        
        
    #Only if I want memory between ticks i need ineer action functino
    @staticmethod
    def approach_target(i_agent: int):
        """
           Move towards target
           Increase speed of thief while approaching target
        """
        def action(i_agent: int):
            pass
        return action
    