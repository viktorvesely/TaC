import random
import numpy as np
from ...state import State

state = State()

class ThiefActions():
    """
        Return only functions not execute them
    """
    """
        - looking_for_target (Different kind of roaming)
            Motivation increases over time and drops after theft attempt (For further consideration, motivation drops after succesfull attempt?)
            when motivation reaches a certain threshold, select_target if 50% motivation is reached start theft process

        - select_target (Select target to approach) calls check_conditions of the cell visibility, motivation. Motivation and visibility (threshold needed for visibility)
            Motivation increases over time and drops after theft attempt (For further consideration, motivation drops after succesfull attempt?)
            
        - approach_target (Move towards target)
            keep checking_conditions while approaching (Check if agent is near target)
            triggers theft when agent reaches "8" distance from target
            
        - theft (Steal from target)
            - 50% prob of succes but could be incremented, for example, with motivation, how many agents are near (this would mean a higher chance of being caught by next tick change of vision)
            - If succesfull
                - Change color momentarily then change back
                - Store event ...
                - Motivation decreases . motivation should be declared in agent as ndarray
                - go back to looking_for_target
                
            
                
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
        
    @staticmethod 
    def check_conditions(i_agent: int):
        """
            Check if agent is near target
            If agent is near target, return True
            Else return False
        """
        agent_coords = state.agent_coords[i_agent, :]
        target_coords = state.target_coords
        if np.max(np.abs(agent_coords - target_coords)) <= 1:
            return True
        return False 
    
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
    