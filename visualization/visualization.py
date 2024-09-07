import pygame
import sys

class Visualization:
    def __init__(self, world):
        pygame.init()
        self.world = world
        self.size = world.size
        self.window_size = 500
        self.cell_size = self.window_size // self.size
        self.colors = {'black': (0, 0, 0), 'white': (255, 255, 255), 'green': (0, 255, 0), 'red': (255, 0, 0)}
        self.window = pygame.display.set_mode((self.window_size, self.window_size))
        pygame.display.set_caption('TaC')
        self.clock = pygame.time.Clock()    
        self.running = True
        self.agents = world.get_agents()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60) # 60 frames per second
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

    def update(self):
        self.world.step()

    def render(self):
        self.window.fill(self.colors['white'])
        for agent in self.agents:
            pygame.draw.circle(self.window,agent.color, (int(agent.pos_x), int(agent.pos_y)), 10)
        pygame.display.flip()

    def __del__(self):
        pygame.quit()
        sys.exit()
    
    