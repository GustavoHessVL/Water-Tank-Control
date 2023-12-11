# tank.py
import pygame

class Tank:
    def __init__(self, x, y, width, height, depth, color=(0, 0, 128)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.depth = depth
        self.water_level = 0
        self.color = color

    def draw(self, screen):
        water_color = (173, 216, 230)  # Dark Blue
        empty_color = (255, 255, 255)  # White
        draw_parallelepiped(screen, water_color, self.x, self.y + self.height - self.water_level, self.width, self.water_level, self.depth, 0)
        draw_parallelepiped(screen, (0,0,0), self.x, self.y + self.height - self.water_level, self.width, self.water_level, self.depth, 2)
        draw_parallelepiped(screen, (0,0,0), self.x, self.y, self.width, self.height, self.depth, 2)

        # pygame.draw.rect(screen, empty_color, (self.x, self.y, self.width, self.height))
        # pygame.draw.rect(screen, water_color, (self.x, self.y + self.height - self.water_level, self.width, self.water_level))
        # pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)

    def update_water_level(self, new_level):
        self.water_level = max(0, min(self.height, new_level))

def draw_parallelepiped(screen, color, x, y, width, height, depth, line):

    depth *= 5/6

    # Definir vértices do paralelepípedo
    vertices = [
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height),
        (x + depth/2, y + height - depth/2),
        (x + width + depth/2, y + height - depth/2),
        (x + width + depth/2, y - depth/2),
        (x + depth/2, y - depth/2)
    ]

    # Definir faces do paralelepípedo
    faces = [
        (0, 1, 2, 3),
        (2, 3, 4, 5), 
        (0, 3, 4, 7),
        (1, 2, 5, 6),
        (4, 5, 6, 7),
        (0, 1, 6, 7)
    ]

    # Desenhar faces
    for face in faces:
        pygame.draw.polygon(screen, color, [vertices[i] for i in face], line)