import pygame
import serial
import threading
from queue import Queue
from tank import Tank

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tank Simulator")

# Create a single tank (bigger in scale, moved to the left)
tank_width = 250  # Original width
tank_height = 400  # Original height
tank_x = 50  # Move it to the left
tank_y = (height - tank_height) // 2  # Center vertically

tank = Tank(tank_x, tank_y, tank_width, tank_height, color=(0, 0, 128))  # Dark Blue

# Slider parameters
slider_width = 20  # Make it vertical
slider_height = 500  # Make it vertical
slider_x = width - 100  # Place it on the right side
slider_y = (height - slider_height) // 2  # Center the slider vertically

# Slider levels and corresponding values (reversed order)
slider_levels = ["Full", "High", "Medium", "Low", "Empty"]
slider_value = "Empty"

# Font setup for slider labels
font = pygame.font.Font(None, 24)

# Serial communication setup
ser = serial.Serial('COM1', 115200, 7, 'O', 1, timeout=1)

# Dictionary to map slider value to binary message
slider_to_binary = {
    "Full": '6',
    "High": '5',
    "Medium": '3',
    "Low": '2',
    "Empty": '0',
}

# Function to draw the vertical slider with a dark blue ball indicator
def draw_slider(screen):
    pygame.draw.rect(screen, (200, 200, 200), (slider_x, slider_y, slider_width, slider_height))
    slider_pos = slider_levels.index(slider_value)
    slider_pos = int((slider_pos / (len(slider_levels) - 1)) * slider_height)

    # Draw a dark blue ball indicator
    ball_radius = 10  # Adjust the radius as needed
    ball_x = slider_x + slider_width / 2
    ball_y = slider_y + slider_pos
    pygame.draw.circle(screen, (0, 0, 128), (int(ball_x), int(ball_y)), ball_radius)

# Update vertical slider value based on mouse position
def update_slider(mouse_y):
    normalized_y = max(0, min(1, (mouse_y - slider_y) / slider_height))
    closest_level = min(range(len(slider_levels)), key=lambda y: abs(y - normalized_y * (len(slider_levels) - 1)))
    return slider_levels[closest_level]

# Function to receive serial data in a separate thread
def receive_serial(data_queue):
    while True:
        try:
            if ser.is_open:
                data = ser.read(9).decode('utf-8').strip()
                if data:  # Check if data is not empty before putting it into the queue
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
                # Update the slider value based on the mouse position
                slider_value = update_slider(event.pos[1])

                # Set the tank's water level
                tank.update_water_level((len(slider_levels) - 1 - slider_levels.index(slider_value)) * 90)
                # Assuming each level represents 50 units, and reversing the order

                # Get the binary message from the dictionary
                binary_data = slider_to_binary.get(slider_value, '0000000')
                print(slider_value, binary_data, binary_data.encode())
                # Send the binary data to the hardware
                ser.write(binary_data.encode())

    # Draw vertical slider
    draw_slider(screen)

    # Draw tank (bigger in scale, moved to the left)
    tank.draw(screen)

    # Draw slider labels (moved even more to the left)
    for i, level in enumerate(slider_levels):
        label = font.render(level, True, (0, 0, 0))
        # Move labels even more to the left
        label_rect = label.get_rect(midleft=(slider_x - 60 - 10 * (width / 800), slider_y + i * (slider_height / (len(slider_levels) - 1))))
        screen.blit(label, label_rect)

   # Check if the data queue is not empty and pop data into the array
    while not data_queue.empty():
        received_data_array.append(data_queue.get_nowait())

        # Print the received data array (you can modify this part as needed)
    print("Received Data Array:", received_data_array)

# Add a delay to avoid high CPU usage
    pygame.time.delay(100)

    pygame.display.flip()

# Close the serial port
ser.close()

# Quit Pygame
pygame.quit()
