# tank.py
import pygame

class Tank:
    def __init__(self, x, y, width, height, color=(0, 0, 128)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.water_level = 0
        self.color = color

    def draw(self, screen):
        water_color = (0, 0, 128)  # Dark Blue
        empty_color = (255, 255, 255)  # White
        pygame.draw.rect(screen, empty_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, water_color, (self.x, self.y + self.height - self.water_level, self.width, self.water_level))
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)

    def update_water_level(self, new_level):
        self.water_level = max(0, min(self.height, new_level))

def draw_tube(screen, x1, y1, x2, y2, tube_color=(0, 0, 0)):
    pygame.draw.line(screen, tube_color, (x1, y1), (x2, y2), 10)

def draw_bomb(screen, x, y, radius, bomb_color=(0, 0, 0)):
    pygame.draw.circle(screen, bomb_color, (x, y), radius)
