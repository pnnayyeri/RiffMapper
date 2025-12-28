# RiffMapper

**RiffMapper** is a lightweight Python tool designed to map the buttons of the **RiffMaster Wireless Guitar** (PS5/PS4) to keyboard buttons on a Windows PC.

Its primary goal is to enable using the guitar controller to play PC games, specifically targeted for **Guitar Hero 3**, which often requires keyboard input or has limited native controller support for modern wireless guitars.

It includes a user-friendly GUI for monitoring inputs and configuring key bindings.

## Features

-   **Controller Support:** Works with standard Gamepads (PS5/Xbox) via Pygame.
-   **Keyboard & Mouse Mapping:** Map buttons to keyboard keys (A-Z, Arrows, Enter, etc.) and Mouse Clicks (Left/Right).
-   **GUI Configuration:** Easy-to-use interface to change mappings on the fly.
-   **Hotplugging:** Detects controllers even if plugged in after the app starts.
-   **Persistence:** Saves your custom mappings to a JSON file.
-   **Low Latency:** Uses a non-blocking event loop for responsiveness.

## Installation

### For Users (Executable)
Download the latest `RiffMapper.exe` from the Releases page (if available) and run it. No Python installation required.

### For Developers (Source)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/RiffMapper.git
    cd RiffMapper
    ```

2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Running from Source
To run the GUI version:
```bash
python riffmapper_gui.py
```

To run the command-line only version (headless):
```bash
python riffmapper.py
```

### Building the Executable
If you want to build a standalone `.exe` file for Windows:

1.  Ensure you have `pyinstaller` installed (included in requirements.txt).
2.  Run the build command:
    ```bash
    pyinstaller --noconfirm --onefile --windowed --name "RiffMapper" --clean riffmapper_gui.py
    ```
3.  The executable will be located in the `dist/` folder.

## Default Mapping (RiffMaster PS5 Layout)

| In-Game Action | Controller Button | Default Key |
| :--- | :--- | :--- |
| **First Fret** | Green (Cross/A) | `Z` |
| **Second Fret** | Red (Circle/B) | `X` |
| **Third Fret** | Yellow (Triangle/Y) | `C` |
| **Fourth Fret** | Blue (Square/X) | `V` |
| **Fifth Fret** | Orange (R1) | `B` |
| **Strum Up** | D-Pad Up | Right Mouse Button |
| **Strum Down** | D-Pad Down | Left Mouse Button |
| **Star Power** | Joystick Button | `Space` |
| **Select** | Share | `Enter` |
| **Pause** | Options | `Esc` |

## Guitar Hero 3 - Keyboard Key Bindings

To ensure the default mapping works correctly with **Guitar Hero 3 (PC)**, go to the in-game **Options > Controller > Keyboard** settings and bind the following keys:

-   **Green Fret:** `Z`
-   **Red Fret:** `X`
-   **Yellow Fret:** `C`
-   **Blue Fret:** `V`
-   **Orange Fret:** `B`
-   **Star Power:** `Space`
-   **Strum Up:** `Right Mouse Button`
-   **Strum Down:** `Left Mouse Button`
-   **Whammy:** *Not supported yet*

### Important Settings & Notes

1.  **Lefty Flip:** You must enable **Lefty Flip** in the game settings.
2.  **Controller Mode:** The RiffMaster controller can be used in either **PS5** or **PS4** modes.
3.  **Avoid Conflicts:** To prevent the game from detecting the controller directly (which can cause input conflicts), **turn off or disconnect the RiffMaster controller** before launching the game. Once the game is open, **turn on or reconnect** the controller.

## License
MIT

