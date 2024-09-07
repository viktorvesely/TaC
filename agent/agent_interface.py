from abc import ABC, abstractmethod

class AgentInterface(ABC):
    @abstractmethod
    def move(self):
        "move function should return the action to be taken by the agent"
    pass