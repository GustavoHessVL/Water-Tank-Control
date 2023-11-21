# main.py
import pygame
from tank import Tank, draw_tube, draw_bomb

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tank Simulator")

# Create tanks
tank1 = Tank(100, 300, 200, 300, color=(0, 0, 128))  # Dark Blue
tank2 = Tank(500, 300, 200, 300, color=(0, 0, 128))  # Dark Blue
tank2.update_water_level(tank2.height)  # Set the second tank to start with full water

# Define tube and bomb positions
tube_start = (tank1.x + tank1.width, tank1.y + tank1.height // 2)
tube_end = (tank2.x, tank2.y + tank2.height // 2)
bomb_position = ((tube_start[0] + tube_end[0]) // 2, (tube_start[1] + tube_end[1]) // 2)

# Define button positions and water levels
button_radius = 25
button_positions = [(75, 25), (200, 25), (325, 25), (450, 25), (575, 25)]
water_levels = [0, 50, 100, 150, 200]  # Define the exact amount of water for each button

# Define button reference levels
button_reference_levels = ["Empty", "Low", "Medium", "High", "Full"]

# Font setup for button labels
font = pygame.font.Font(None, 24)

# Main game loop
running = True
while running:
    screen.fill((255, 255, 255))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, pos in enumerate(button_positions):
                if (
                    pos[0] - button_radius < event.pos[0] < pos[0] + button_radius
                    and pos[1] - button_radius < event.pos[1] < pos[1] + button_radius
                ):
                    # Set the exact water level based on the button clicked
                    tank1.update_water_level(water_levels[i])
                    tank2.update_water_level(tank2.height - water_levels[i])  # Set tank 2 based on the complementary amount

    # Draw tanks
    tank1.draw(screen)
    tank2.draw(screen)

    # Draw tube
    draw_tube(screen, tube_start[0], tube_start[1], tube_end[0], tube_end[1])

    # Draw bomb
    draw_bomb(screen, bomb_position[0], bomb_position[1], radius=15)

    # Draw round buttons with labels
    for i, pos in enumerate(button_positions):
        pygame.draw.circle(screen, (0, 128, 0), pos, button_radius)
        pygame.draw.circle(screen, (0, 0, 0), pos, button_radius, 2)
        
        # Draw button labels
        label = font.render(button_reference_levels[i], True, (0, 0, 0))
        label_rect = label.get_rect(center=(pos[0], pos[1] + button_radius + 15))
        screen.blit(label, label_rect)

    pygame.display.flip()

# Quit Pygame
pygame.quit()