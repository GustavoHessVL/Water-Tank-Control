import pygame
import threading
import re
from serial import Serial 
from queue import Queue
from tank import Tank
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Physical Constants
TANK_HEIGHT = 24.1

# Initialize Pygame
pygame.init()

# Set up display
width, height = 1400, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Digital Twin - Tank Simulator")

# Create a single tank
tank_width = 250
tank_height = 400
tank_x = width/2 - tank_width/2 - 400
tank_y = height/2 - tank_height/2  # Adjusted position to be at the top
tank = Tank(tank_x, tank_y, tank_width, tank_height, tank_width/2, color=(0, 0, 128))

# Slider parameters
slider_width = 10
slider_height = tank_height * (20 - 6) / TANK_HEIGHT
slider_x = 100  # Adjusted to leave space on the right
slider_y = height/2 - tank_height/2 + tank_height * 4 / TANK_HEIGHT  # Adjusted position to be at the top
slider_levels = ["20cm", "18cm", "16cm", "14cm", "12cm", "10cm", "8cm", "6cm"]

slider_value = "6cm"

# Font setup for slider labels
font = pygame.font.Font(None, 24)

# Serial communication setup
ser = Serial("/dev/ttyUSB0", 115200, 7, 'O', 1, timeout=1)

# Dictionary to map slider value to binary message
slider_to_binary = {
    "20cm": '7',
    "18cm": '6',
    "16cm": '5',
    "14cm": '4',
    "12cm": '3',
    "10cm": '2',
    "8cm": '1',
    "6cm": '0',
}

# Function to draw the vertical slider with a dark blue ball indicator
def draw_slider(screen):
    pygame.draw.rect(screen, (200, 200, 200), (slider_x, slider_y, slider_width, slider_height))
    slider_pos = slider_levels.index(slider_value)
    slider_pos = int((slider_pos / (len(slider_levels) - 1)) * slider_height)

    ball_radius = 7.5
    ball_x = slider_x + slider_width / 2
    ball_y = slider_y + slider_pos
    pygame.draw.circle(screen, (0, 0, 128), (int(ball_x), int(ball_y)), ball_radius)

def draw_water_level_indicator(screen, x, y, water_level):
    font = pygame.font.Font(None, 24)
    text = font.render(f"{f'{water_level:.1f}'.replace('.', ',')} cm", True, (0, 0, 0))
    text_rect = text.get_rect(midtop=(x + 30, y + slider_height * (20 - water_level) / (20 - 6) - 12))
    screen.blit(text, text_rect)

# Update vertical slider value base d on mouse position
def update_slider(mouse_y):
    normalized_y = max(0, min(1, (mouse_y - slider_y) / slider_height))
    closest_level = min(range(len(slider_levels)), key=lambda y: abs(y - normalized_y * (len(slider_levels) - 1)))
    return slider_levels[closest_level]

def update_graph(ax, data_array):
    ax.clear()
    ax.plot(range(len(data_array)), data_array, marker='o', linestyle='-')
    ax.set_xlim(max(0, len(data_array) - 200), len(data_array))
    ax.set_ylim(0, TANK_HEIGHT)
    ax.set_title("Tank Water Level Over Time")
    ax.set_xlabel("Measure")
    ax.set_ylabel("Water Level (cm)")

def is_valid_string(s):
    pattern = r'^\d{3},\d{1,}cm*$'
    return bool(re.match(pattern, s))

# Function to receive serial data in a separate thread
def receive_serial(data_queue):
    while True:
        try:
            if ser.is_open:
                data = ser.readline().decode('utf-8').strip()
                print(f"Serial data: {data}")
                if is_valid_string(data):
                    data_queue.put(data)
            else:
                print("Serial port is not open.")
        except BaseException as e:
            print(e)
        pygame.time.delay(250)  # Add a delay to avoid high CPU usage

# Start the thread for receiving serial data
data_queue = Queue()
data_thread = threading.Thread(target=receive_serial, args=(data_queue,))
data_thread.daemon = True
data_thread.start()

# Create a mock queue
mock_data_queue = Queue()

# Set up matplotlib for real-time graph
fig, ax = plt.subplots(figsize=(8, 5))  # Adjust the figsize parameter as needed
canvas = FigureCanvas(fig)

# Main game loop
running = True
received_data_array = []  # Array to store received serial data
while running:
    screen.fill((255, 255, 255))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if (
                slider_x - 5 < event.pos[0] < slider_x + slider_width + 5
                and slider_y - 5 < event.pos[1] < slider_y + slider_height + 5
            ):
                slider_value = update_slider(event.pos[1])
                binary_data = slider_to_binary.get(slider_value, '0000000')
                print(slider_value, binary_data, binary_data.encode())
                ser.write(binary_data.encode())

    if data_queue.qsize() >= 1:
            data = data_queue.get()

            # Replace comma with period and extract the relevant part, e.g., "013.0"
            important_data = float(data.replace(',', '.')[1:5])
            
            if important_data > 4 and important_data < 20:
                received_data_array.append((TANK_HEIGHT-float(important_data)))

    # Draw tank (bigger in scale, moved to the left) based on the last value in received_data_array
    if received_data_array:
        last_value = received_data_array[-1] * 400/TANK_HEIGHT
        tank.update_water_level(last_value)  # Set the tank's water level based on the last value in the array
        draw_water_level_indicator(screen, tank_x + tank_width + tank_width/4, slider_y, received_data_array[-1])

    # Draw tank
    tank.draw(screen)

    # Draw slider labels (moved even more to the left)
    for i, level in enumerate(slider_levels):
        label = font.render(level, True, (0, 0, 0))
        label_rect = label.get_rect(
            midleft=(slider_x - 80, slider_y + i * (slider_height / (len(slider_levels) - 1))))
        screen.blit(label, label_rect)


    # Update and render the real-time graph
    update_graph(ax, received_data_array)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()
    graph_surface = pygame.image.fromstring(raw_data, size, "RGB")
    screen.blit(graph_surface, (width - 800, 50))  # Adjust the position as needed

    # Draw slider
    draw_slider(screen)

    # pygame.time.delay(100)
    pygame.display.flip()

# Close the serial port
ser.close()

# Quit Pygame
pygame.quit()
