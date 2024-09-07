from world.world_interface import WorldInterface

class World(WorldInterface):
    def __init__(self, size):
        self.size = size
        self.agents = []
        self.obstacles = []
    
    def add_agent(self, agent):
        self.agents.append(agent)
    
    def step(self):
        for agent in self.agents:
            agent.move()
    
    def get_agents(self):
        return self.agents