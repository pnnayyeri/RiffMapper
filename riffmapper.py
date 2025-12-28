import pygame
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import time

class RiffMapper:
    def __init__(self):
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        self.joystick = None
        self.joystick_id = None
        
        # Initialize Pygame and Joystick
        pygame.init()
        pygame.joystick.init()
        
        # Check for existing controllers immediately
        self.check_existing_controllers()
        
        # PS5 Controller Mapping (Standard Layout)
        # Button indices vary by OS/Driver, these are common for Windows
        self.mapping = {
            0: 'z',          # Green Button
            1: 'x',          # Red Button
            3: 'c',          # Yellow Button
            2: 'v',          # Blue Button
            9: 'b',          # Orange Button
            4: Key.enter,    # Share
            6: Key.esc,      # Options
            7: Key.space,    # Joystick Button
            11: Button.right, # D-Pad Up -> LMB
            12: Button.left,# D-Pad Down -> RMB
            13: Key.left,    # D-Pad Left
            14: Key.right,   # D-Pad Right
        }

    def check_existing_controllers(self):
        if pygame.joystick.get_count() > 0:
            self.connect_controller(0)
        else:
            print("No controller found at startup. Waiting for connection...")

    def connect_controller(self, device_index):
        if self.joystick is None:
            try:
                self.joystick = pygame.joystick.Joystick(device_index)
                self.joystick.init()
                self.joystick_id = self.joystick.get_instance_id()
                print(f"Connected: {self.joystick.get_name()}")
            except pygame.error as e:
                print(f"Failed to connect to controller: {e}")

    def disconnect_controller(self, instance_id):
        if self.joystick and self.joystick_id == instance_id:
            print(f"Disconnected: {self.joystick.get_name()}")
            self.joystick.quit()
            self.joystick = None
            self.joystick_id = None

    def run(self):
        print("Starting RiffMapper (Pygame)... Press Ctrl+C to stop.")
        running = True
        try:
            while running:
                # Pump events from queue
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        
                    elif event.type == pygame.JOYDEVICEADDED:
                        print(f"New device detected: Index {event.device_index}")
                        self.connect_controller(event.device_index)
                        
                    elif event.type == pygame.JOYDEVICEREMOVED:
                        print(f"Device removed: Instance {event.instance_id}")
                        self.disconnect_controller(event.instance_id)

                    elif event.type == pygame.JOYBUTTONDOWN:
                        if self.joystick and event.instance_id == self.joystick_id:
                            if event.button in self.mapping:
                                action = self.mapping[event.button]
                                print(f"Pressed: {event.button} -> {action}")
                                if isinstance(action, Button):
                                    self.mouse.press(action)
                                else:
                                    self.keyboard.press(action)
                            
                    elif event.type == pygame.JOYBUTTONUP:
                        if self.joystick and event.instance_id == self.joystick_id:
                            if event.button in self.mapping:
                                action = self.mapping[event.button]
                                print(f"Released: {event.button} -> {action}")
                                if isinstance(action, Button):
                                    self.mouse.release(action)
                                else:
                                    self.keyboard.release(action)
                            
                # Small sleep to prevent high CPU usage
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            if self.joystick:
                self.joystick.quit()
            pygame.quit()

if __name__ == "__main__":
    try:
        mapper = RiffMapper()
        mapper.run()
    except Exception as e:
        print(f"Error: {e}")

