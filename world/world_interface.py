from abc import ABC, abstractmethod

class WorldInterface(ABC):
    @abstractmethod
    def add_agent(self, agent):
        "add an agent to the world"
    
    @abstractmethod
    def step(self):
        "move all agents in the world"
    
    @abstractmethod
    def get_agents(self):
        "return all agents in the world"