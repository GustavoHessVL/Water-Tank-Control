import pygame
import serial
import threading
from queue import Queue
from tank import Tank
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Initialize Pygame
pygame.init()

# Set up display
width, height = 1400, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tank Simulator")

# Create a single tank (bigger in scale, moved to the left)
tank_width = 250
tank_height = 400
tank_x = width/2 - tank_width/2 + 100
tank_y = 50  # Adjusted position to be at the top
tank = Tank(tank_x, tank_y, tank_width, tank_height, color=(0, 0, 128))

# Slider parameters
slider_width = 20
slider_height = 540
slider_x = width - 120  # Adjusted to leave space on the right
slider_y = 20  # Adjusted position to be at the top
slider_levels = ["Full", "High", "Medium-High", "Medium", "Medium-Low", "Low", "Very Low", "Empty"]

slider_value = "Empty"

# Font setup for slider labels
font = pygame.font.Font(None, 24)

# Serial communication setup
ser = serial.Serial('COM1', 115200, 7, 'O', 1, timeout=1)

# Dictionary to map slider value to binary message
slider_to_binary = {
    "Full": '7',
    "High": '6',
    "Medium-High": '5',
    "Medium": '4',
    "Medium-Low": '3',
    "Low": '2',
    "Very Low": '1',
    "Empty": '0',
}

# Function to draw the vertical slider with a dark blue ball indicator
def draw_slider(screen):
    pygame.draw.rect(screen, (200, 200, 200), (slider_x, slider_y, slider_width, slider_height))
    slider_pos = slider_levels.index(slider_value)
    slider_pos = int((slider_pos / (len(slider_levels) - 1)) * slider_height)

    ball_radius = 10
    ball_x = slider_x + slider_width / 2
    ball_y = slider_y + slider_pos
    pygame.draw.circle(screen, (0, 0, 128), (int(ball_x), int(ball_y)), ball_radius)


# Update vertical slider value based on mouse position
def update_slider(mouse_y):
    normalized_y = max(0, min(1, (mouse_y - slider_y) / slider_height))
    closest_level = min(range(len(slider_levels)), key=lambda y: abs(y - normalized_y * (len(slider_levels) - 1)))
    return slider_levels[closest_level]

def update_graph(ax, data_array):
    ax.clear()
    ax.plot(range(len(data_array)), data_array, marker='o', linestyle='-')
    ax.set_xlim(max(0, len(data_array) - 20), len(data_array))
    ax.set_ylim(0, max(data_array) + 10)
    ax.set_title("Tank Water Level Over Time")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Water Level")

# Function to receive serial data in a separate thread
def receive_serial(data_queue):
    while True:
        try:
            if ser.is_open:
                data = ser.read(9).decode('utf-8').strip()
                data_queue.put(data)
                print(f"Serial data: {data}")
            else:
                print("Serial port is not open.")
        except BaseException as e:
            print(e)
        pygame.time.delay(100)  # Add a delay to avoid high CPU usage

# Start the thread for receiving serial data
data_queue = Queue()
data_thread = threading.Thread(target=receive_serial, args=(data_queue,))
data_thread.daemon = True
data_thread.start()

# Function to simulate receiving data in a separate thread, it is a mock-up
def simulate_receive_serial(mock_data_queue):
    # for data in ["100", "150", "200", "180", "250", "275", "295", "305", "320", "340", "360", "380", "392", "400"]:
    #     pygame.time.delay(50)
    #     mock_data_queue.put(data)

        # Function to simulate receiving data in a separate thread, it is a mock-up
    char_array = ["0", "1", "3", ",", "0", "c", "m", "#",
                  "0", "1", "3", ",", "5", "c", "m", "#",
                  "0", "1", "4", ",", "0", "c", "m", "#",
                  "0", "1", "4", ",", "5", "c", "m", "#",
                  "0", "1", "5", ",", "0", "c", "m", "#"
                  ]
    for char in char_array:
        pygame.time.delay(50)
        mock_data_queue.put(char)
    mock_data_queue.put("")  # Add an empty string to simulate receiving an empty data

# Create a mock queue
mock_data_queue = Queue()

# Set up matplotlib for real-time graph
fig, ax = plt.subplots(figsize=(5, 3))  # Adjust the figsize parameter as needed
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


    # simulate_receive_serial(mock_data_queue)  # Uncomment this line to use mock data

    # if not mock_data_queue.empty():
    #     data = mock_data_queue.get()  # Uncomment this line to use mock data
    #     if data:  # Only append non-empty data to the array
    #         received_data_array.append(int(data))
    # print("Received Data Array:", received_data_array)


    #IMPORTANT, IF NOT MOCKING UP DATA, COMMENT FROM 133 UNTILL 139, OTHERWISE UNCOMMENT FROM 145 UNTILL 153    


    if data_queue.qsize() >= 8:
            data = ""
            for _ in range(8):
                data += data_queue.get()

            # Replace comma with period and extract the relevant part, e.g., "013.0"
            important_data = data.replace(',', '.')[1:5]
            received_data_array.append((20-float(important_data))*20)
            print("Received Data Array:", received_data_array)

    # Draw tank (bigger in scale, moved to the left) based on the last value in received_data_array
    if received_data_array:
        last_value = received_data_array[-1]
        tank.update_water_level(last_value)  # Set the tank's water level based on the last value in the array

    # Draw tank
    tank.draw(screen)

    # Draw slider labels (moved even more to the left)
    for i, level in enumerate(slider_levels):
        label = font.render(level, True, (0, 0, 0))
        label_rect = label.get_rect(
            midleft=(slider_x - 100 - 10 * (width / 800), slider_y + i * (slider_height / (len(slider_levels) - 1))))
        screen.blit(label, label_rect)

    # Update and render the real-time graph
    update_graph(ax, received_data_array)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()
    graph_surface = pygame.image.fromstring(raw_data, size, "RGB")
    screen.blit(graph_surface, (50, 100))  # Adjust the position as needed

    # Draw slider
    draw_slider(screen)

    # pygame.time.delay(100)
    pygame.display.flip()

# Close the serial port
ser.close()

# Quit Pygame
pygame.quit()
