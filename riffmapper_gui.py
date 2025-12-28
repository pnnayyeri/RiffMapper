import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import pygame
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import threading
import sys
import os
import json

# --- Default Configuration ---
DEFAULT_MAPPING = {
    "0": "z",           # Green Button
    "1": "x",           # Red Button
    "3": "c",           # Yellow Button
    "2": "v",           # Blue Button
    "9": "b",           # Orange Button
    "4": "Key.enter",   # Share
    "6": "Key.esc",     # Options
    "7": "Key.space",   # Joystick Button
    "11": "Button.right",# D-Pad Up -> RMB
    "12": "Button.left", # D-Pad Down -> LMB
    "13": "Key.left",   # D-Pad Left
    "14": "Key.right"   # D-Pad Right
}

BUTTON_NAMES = {
    0: "Green Button (0)",
    1: "Red Button (1)",
    2: "Blue Button (2)",
    3: "Yellow Button (3)",
    4: "Share (4)",
    6: "Options (6)",
    7: "Joystick Btn (7)",
    9: "Orange Button (9)",
    11: "D-Pad Up (11)",
    12: "D-Pad Down (12)",
    13: "D-Pad Left (13)",
    14: "D-Pad Right (14)"
}

AVAILABLE_KEYS = [
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", 
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "space", "return", "escape", "backspace", "tab",
    "Key.up", "Key.down", "Key.left", "Key.right",
    "Key.enter", "Key.esc", "Key.space", "Key.tab", 
    "Key.shift", "Key.ctrl", "Key.alt",
    "Button.left", "Button.right", "Button.middle"
]

CONFIG_FILE = "key_mapping.json"

# Order and labels for the UI rows
UI_ROW_ORDER = [
    (0, "First Fret"),
    (1, "Second Fret"),
    (3, "Third Fret"),
    (2, "Fourth Fret"),
    (9, "Fifth Fret"),
    (4, "Confirm/Select"),
    (6, "Menu/Pause"),
    (7, "Star Power"),
    (11, "Strum Up/Up"),
    (12, "Strum Down/Down"),
    (13, "Left"),
    (14, "Right")
]

class RiffMapperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RiffMapper v1.0")
        self.root.geometry("600x500") # Increased size for 3 columns
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Controllers
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        self.joystick = None
        self.joystick_id = None
        self.mapping = {}

        # Load Config
        self.load_config()

        # UI Setup
        self.setup_ui()

        # Initialize Pygame
        pygame.init()
        pygame.joystick.init()
        self.check_existing_controllers()
        
        # Start the update loop
        self.running = True
        self.root.after(10, self.update_loop)

    def load_config(self):
        """Load mapping from JSON or use defaults."""
        config_data = DEFAULT_MAPPING.copy()
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    saved_data = json.load(f)
                    # Merge saved data with defaults (in case of missing keys)
                    config_data.update(saved_data)
                    self.log_internal("Configuration loaded.")
            except Exception as e:
                self.log_internal(f"Error loading config: {e}")

        # Convert string keys to proper objects for runtime use
        self.mapping = {} # Internal mapping with objects
        self.str_mapping = {} # String representation for UI/Save
        
        for btn_id_str, action_str in config_data.items():
            btn_id = int(btn_id_str)
            self.str_mapping[btn_id] = action_str
            self.mapping[btn_id] = self.parse_action(action_str)

    def save_config(self):
        """Save current string mapping to JSON."""
        # Update str_mapping from UI variables
        for btn_id, var in self.ui_vars.items():
            self.str_mapping[btn_id] = var.get()
            # Update runtime mapping immediately
            self.mapping[btn_id] = self.parse_action(var.get())

        # Convert integer keys to strings for JSON compatibility
        json_data = {str(k): v for k, v in self.str_mapping.items()}
        
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(json_data, f, indent=4)
            messagebox.showinfo("Success", "Configuration saved successfully!")
            self.log_internal("Configuration saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def parse_action(self, action_str):
        """Convert string representation to pynput object."""
        if action_str.startswith("Key."):
            return getattr(Key, action_str.split(".")[1], None)
        elif action_str.startswith("Button."):
            return getattr(Button, action_str.split(".")[1], None)
        else:
            return action_str # It's a character string

    def setup_ui(self):
        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

        # Tab 1: Monitor
        self.tab_monitor = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_monitor, text="Monitor")
        self.setup_monitor_tab()

        # Tab 2: Settings
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="Key Mapping")
        self.setup_settings_tab()

    def setup_monitor_tab(self):
        # Status
        self.status_label = tk.Label(self.tab_monitor, text="Initializing...", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=15)

        # Log
        lbl = tk.Label(self.tab_monitor, text="Event Log:")
        lbl.pack(anchor='w', padx=10)
        
        self.log_area = scrolledtext.ScrolledText(self.tab_monitor, width=55, height=15, state='disabled')
        self.log_area.pack(pady=5, padx=10, expand=True, fill='both')

        btn_clear = ttk.Button(self.tab_monitor, text="Clear Log", command=self.clear_log)
        btn_clear.pack(pady=5)

    def setup_settings_tab(self):
        # Scrollable container for settings
        canvas = tk.Canvas(self.tab_settings)
        scrollbar = ttk.Scrollbar(self.tab_settings, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Config Rows
        self.ui_vars = {}
        
        # Header
        ttk.Label(scrollable_frame, text="In-Game Action", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        ttk.Label(scrollable_frame, text="Controller Button", font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=10, pady=10, sticky='w')
        ttk.Label(scrollable_frame, text="Mapped Action", font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=10, pady=10, sticky='w')

        row = 1
        
        # Track which IDs we've displayed to handle any extras
        displayed_ids = set()

        # Render rows in the specific order requested
        for btn_id, game_action in UI_ROW_ORDER:
            displayed_ids.add(btn_id)
            
            # In-Game Action Label
            ttk.Label(scrollable_frame, text=game_action).grid(row=row, column=0, padx=10, pady=5, sticky='w')
            
            # Button Name Label
            name = BUTTON_NAMES.get(btn_id, f"Button {btn_id}")
            ttk.Label(scrollable_frame, text=name).grid(row=row, column=1, padx=10, pady=5, sticky='w')
            
            # Action Selector
            current_val = self.str_mapping.get(btn_id, "")
            var = tk.StringVar(value=current_val)
            self.ui_vars[btn_id] = var
            
            # Combobox with filtering/entry capability
            combo = ttk.Combobox(scrollable_frame, textvariable=var, values=AVAILABLE_KEYS, width=15)
            combo.grid(row=row, column=2, padx=10, pady=5)
            
            row += 1

        # Render any other buttons that might exist in the config but aren't in the ordered list
        remaining_ids = sorted(list(set(self.str_mapping.keys()) - displayed_ids))
        for btn_id in remaining_ids:
            # Generic Label
            ttk.Label(scrollable_frame, text="Other").grid(row=row, column=0, padx=10, pady=5, sticky='w')

            name = BUTTON_NAMES.get(btn_id, f"Button {btn_id}")
            ttk.Label(scrollable_frame, text=name).grid(row=row, column=1, padx=10, pady=5, sticky='w')
            
            current_val = self.str_mapping.get(btn_id, "")
            var = tk.StringVar(value=current_val)
            self.ui_vars[btn_id] = var
            
            combo = ttk.Combobox(scrollable_frame, textvariable=var, values=AVAILABLE_KEYS, width=15)
            combo.grid(row=row, column=2, padx=10, pady=5)
            
            row += 1

        # Save Button at the bottom (outside scrollable area)
        btn_frame = ttk.Frame(self.tab_settings)
        btn_frame.pack(side="bottom", fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Save Configuration", command=self.save_config).pack()
        ttk.Label(btn_frame, text="* Restart not required after saving", font=('Arial', 8, 'italic')).pack()

    def log(self, message):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')
        
    def log_internal(self, message):
        # Helper that doesn't crash if UI isn't ready
        try:
            self.log(message)
        except:
            print(message)

    def clear_log(self):
        self.log_area.configure(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.configure(state='disabled')

    def set_status(self, text, color="black"):
        self.status_label.config(text=text, fg=color)

    def check_existing_controllers(self):
        if pygame.joystick.get_count() > 0:
            self.connect_controller(0)
        else:
            self.set_status("No Controller Found", "red")
            self.log_internal("Waiting for controller connection...")

    def connect_controller(self, device_index):
        if self.joystick is None:
            try:
                self.joystick = pygame.joystick.Joystick(device_index)
                self.joystick.init()
                self.joystick_id = self.joystick.get_instance_id()
                name = self.joystick.get_name()
                self.set_status(f"Connected: {name}", "green")
                self.log_internal(f"Connected to {name}")
            except pygame.error as e:
                self.log_internal(f"Connection failed: {e}")

    def disconnect_controller(self, instance_id):
        if self.joystick and self.joystick_id == instance_id:
            name = self.joystick.get_name()
            self.set_status("Disconnected", "red")
            self.log_internal(f"Disconnected from {name}")
            self.joystick.quit()
            self.joystick = None
            self.joystick_id = None

    def update_loop(self):
        if not self.running:
            return

        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pass # Handled by window close
                    
                elif event.type == pygame.JOYDEVICEADDED:
                    self.connect_controller(event.device_index)
                    
                elif event.type == pygame.JOYDEVICEREMOVED:
                    self.disconnect_controller(event.instance_id)

                elif event.type == pygame.JOYBUTTONDOWN:
                    if self.joystick and event.instance_id == self.joystick_id:
                        if event.button in self.mapping:
                            action = self.mapping[event.button]
                            action_name = self.str_mapping.get(event.button, str(action))
                            self.log(f"Pressed: {event.button} -> {action_name}")
                            
                            if isinstance(action, Button):
                                self.mouse.press(action)
                            elif isinstance(action, Key):
                                self.keyboard.press(action)
                            elif isinstance(action, str):
                                # It's a character
                                self.keyboard.press(action)
                        
                elif event.type == pygame.JOYBUTTONUP:
                    if self.joystick and event.instance_id == self.joystick_id:
                        if event.button in self.mapping:
                            action = self.mapping[event.button]
                            action_name = self.str_mapping.get(event.button, str(action))
                            self.log(f"Released: {event.button} -> {action_name}")
                            
                            if isinstance(action, Button):
                                self.mouse.release(action)
                            elif isinstance(action, Key):
                                self.keyboard.release(action)
                            elif isinstance(action, str):
                                self.keyboard.release(action)
                                
        except Exception as e:
            self.log(f"Error: {e}")

        self.root.after(10, self.update_loop)

    def on_close(self):
        self.running = False
        if self.joystick:
            self.joystick.quit()
        pygame.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RiffMapperGUI(root)
    root.mainloop()

