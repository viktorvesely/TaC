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
        #print("Thief- Starting Looking for target")
        #Motivation increases over time
        state.agent_motivations[i_agent] += 0.01
        print("Thief- Motivation: ", state.agent_motivations[i_agent])
        if ThiefActions._check_conditions(i_agent):
            return ThiefActions.look_for_target
        return ThiefActions.start_looking_for_target 
     
    @staticmethod
    def start_approaching_target(i_agent: int):
        return ThiefActions.approach_target(i_agent)
    
    @staticmethod
    def look_for_target(i_agent: int):
        """
           If appropiate target found, start aproaching to target calling ThiefActions.approach_target
           Else keep looking for target  
        """
        #print("Thief- Looking for target")
        agents_in_vision = state.agents_in_vision[i_agent, :]
        agent_mask = agents_in_vision != -1
        agents = agents_in_vision[agent_mask]
        
        agents_in_vision_coords = state.agent_coords[agents, :]
        
        for agent in agents_in_vision_coords:
            if (-state.world.vision.values[agent[0], agent[1]] + state.agent_motivations[i_agent]) < 0:
                return ThiefActions.approach_target(i_agent, agent)
            
        return ThiefActions.look_for_target
        
    
    
    #Only if I want memory between ticks i need ineer action functino
    @staticmethod
    def approach_target(i_agent: int, target_i: int):
        """
           Move towards target
           Increase speed of thief while approaching target
        """
        print("Thief- Approaching target")
        
        #While approaching change target and agent to yellow
        state.agent_colors[i_agent, :] = [255, 255, 0]
        state.agent_colors[target_i, :] = [255, 255, 0]
        
        #Increase thief speed
        state.agent_speed[i_agent, :] = 0.18
        
        def action(i_agent: int):
            #Calculating current distance to target
            delta = state.agent_position[target_i, :] - state.agent_position[i_agent,:]
            print("Thief- Distance to target: ", np.linalg.norm(delta))
            #If distance is less than 8, start theft
            if np.linalg.norm(delta) < 600:
                return ThiefActions.theft(i_agent, target_i)
            return action
        
        return action
    
    def theft(i_agent: int, target_i: int):
        """
            Steal from target
        """
        print("Thief- Stealing from target")
        
        #50% chance of succesfull theft
        if random.random() > 0.5:
            #Change color momentarily
            state.agent_colors[i_agent, :] = [0, 0, 255]
            #Store event
            #Motivation decreases
            state.agent_motivations[i_agent] -= 0.1
            #Go back to looking for target
            return ThiefActions.start_looking_for_target(i_agent)
        else:
            #If theft is not succesfull, go back to looking for target
            return ThiefActions.start_looking_for_target(i_agent)
    
    def _check_conditions(i_agent: int) -> bool:
        """
            Check if conditions are met to start theft process , if motivation, visibility > threshold
        """
        motivation = state.agent_motivations[i_agent,:]
        return motivation >= 0.5