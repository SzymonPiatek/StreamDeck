import functools
import re
import subprocess

import keyboard

from src.device.device import Device
from src.system.system.system import System


def handle_subprocess_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except subprocess.CalledProcessError as e:
            print(f"DEBUG: Błąd w funkcji {func.__name__}: {e}")

    return wrapper


class MacOS(System):
    def __init__(self, application):
        super().__init__(name="MacOS")

        self.application = application

        self.functions = [
            # Audio
            {"name": "Volume +", "function": self.volume_up},
            {"name": "Volume -", "function": self.volume_down},
            {"name": "Mute/Unmute", "function": self.mute_unmute},
            # Apple Music
            {"name": "Toggle Apple music", "function": self.toggle_apple_music},
            {"name": "Next track Apple music", "function": self.next_track_apple_music},
            {"name": "Previous track Apple music", "function": self.previous_track_apple_music},
            # Spotify
            {"name": "Toggle Spotify", "function": self.toggle_spotify},
            {"name": "Next track spotify", "function": self.next_track_spotify},
            {"name": "Previous track spotify", "function": self.previous_track_spotify},
            {"name": "Open Spotify", "function": self.open_spotify},
            # Brightness
            {"name": "Brightness +", "function": self.increase_brightness},
            {"name": "Brightness -", "function": self.decrease_brightness},
            # Utils
            {"name": "Toggle bar", "function": self.toggle_bar},
            {"name": "Open calculator", "function": self.open_calculator},
            {"name": "Open terminal", "function": self.open_terminal},
            {"name": "Open google chrome", "function": self.open_google_chrome},
            {"name": "Open finder", "function": self.open_finder},
        ]

    def get_active_input_device(self):
        result = subprocess.getoutput("ioreg -r -c IOHIDDevice")

        devices = []
        current_device = None

        for line in result.split("\n"):
            line = line.strip()

            if '"Product"' in line:
                match = re.search(r'"Product" = "(.*?)"', line)
                if match:
                    current_device = match.group(1)

            if current_device and (
                "Keyboard" in current_device or "Trackpad" in current_device or "Mouse" in current_device
            ):
                devices.append(current_device)

        if devices:
            return devices[0]

        return None

    def recognize_devices(self):
        devices = [self.get_builtin_keyboard()]

        usb_devices = self.get_usb_devices()
        bluetooth_devices = self.get_bluetooth_devices()

        devices.extend(usb_devices)
        devices.extend(bluetooth_devices)

        return devices

    def get_usb_devices(self):
        result = subprocess.getoutput("system_profiler SPUSBDataType")
        devices = []

        current_device = None

        for line in result.split("\n"):
            line = line.strip()

            if line.startswith("Product Name:"):
                device_name = line.split(":")[1].strip()
                current_device = Device(name=device_name, device_type="USB")

            elif line.startswith("Product ID:") and current_device:
                match = re.search(r"Product ID: 0x(\w+)", line)
                if match:
                    current_device.device_id = int(match.group(1), 16)

            if current_device and current_device.name:
                devices.append(current_device)
                current_device = None

        return devices

    def get_bluetooth_devices(self):
        result = subprocess.getoutput("system_profiler SPBluetoothDataType")

        devices = []
        inside_connected_section = False
        current_device_name = None
        current_device_data = {}

        for line in result.split("\n"):
            line = line.strip()

            if line.startswith("Connected:"):
                inside_connected_section = True
                continue

            if line.startswith("Not Connected:"):
                break

            if inside_connected_section:
                device_match = re.match(r"^([A-Za-z0-9 ()-_]+):$", line)
                if device_match:
                    if current_device_name:
                        devices.append({"name": current_device_name, "data": current_device_data})

                    current_device_name = device_match.group(1)
                    current_device_data = {}

                else:
                    data_match = re.match(r"^(.+?):\s(.+)$", line)
                    if data_match:
                        key = data_match.group(1).strip()
                        value = data_match.group(2).strip()

                        key = key.lower().replace(" ", "_")

                        if key == "minor_type":
                            key = "minor_type"

                        current_device_data[key] = value

        if current_device_name:
            devices.append({"name": current_device_name, "data": current_device_data})

        final_devices = []
        for device in devices:
            new_device = Device(
                name=device["name"], device_type="Bluetooth", device_id=device["data"].get("product_id")
            )
            final_devices.append(new_device)
        return final_devices

    def get_builtin_keyboard(self):
        result = subprocess.getoutput("ioreg -r -c AppleEmbeddedKeyboard -d 1 | grep -i 'Product'")

        if result:
            device_name = None
            device_id = None
            device_type = "Builtin"

            for line in result.split("\n"):
                line = line.strip()

                if '"Product"' in line:
                    match = re.search(r'"Product" = "(.*?)"', line)
                    if match:
                        device_name = match.group(1)

                if '"ProductID"' in line:
                    match = re.search(r'"ProductID" = (\d+)', line)
                    if match:
                        device_id = int(match.group(1))

            builtin_device = Device(name=device_name, device_id=device_id, device_type=device_type)

            return builtin_device
        return None

    def device_listener(self):
        try:
            keyboard.on_press(self.application.on_key_press)
            keyboard.wait()
        except Exception as e:
            print(f"DEBUG: Błąd podczas nasłuchiwania klawiszy: {e}")

    def listen_for_key(self, macro, key_button):
        key_button.setText("Naciśnij klawisz...")
        key_button.setEnabled(False)

        def on_key_press(event):
            new_key = event.name
            keyboard.unhook_all()

            for existing_macro in self.application.macros:
                if existing_macro["key"] == new_key:
                    key_button.setText(macro["key"])
                    key_button.setEnabled(True)
                    return

            old_key = macro["key"]
            macro["key"] = new_key
            key_button.setText(new_key)
            key_button.setEnabled(True)

            self.application.update_macro_key(old_key, new_key)

        keyboard.hook(on_key_press)
        return

    @handle_subprocess_error
    def open_app(self, app_name):
        subprocess.run(["open", "-a", app_name], check=True)

    @handle_subprocess_error
    def open_url(self, url):
        subprocess.run(["open", url], check=True)

    @handle_subprocess_error
    def execture_osascript(self, command):
        subprocess.run(["osascript", "-e", command], check=False)

    # Audio
    def volume_up(self):
        self.execture_osascript(
            command="set volume output volume (output volume of (get volume settings) + 5) --100 max"
        )

    def volume_down(self):
        self.execture_osascript(
            command="set volume output volume (output volume of (get volume settings) - 5) --100 max"
        )

    def mute_unmute(self):
        self.execture_osascript(
            command="""
            set currentMute to output muted of (get volume settings)
            if currentMute then
                set volume output muted false
            else
                set volume output muted true
            end if
        """
        )

    # Apple Music
    def toggle_apple_music(self):
        self.execture_osascript(
            command="""
        tell application "Music"
            if player state is playing then
                pause
            else
                play
            end if
        end tell
        """
        )

    def next_track_apple_music(self):
        self.execture_osascript(command='tell application "Music" to next track')

    def previous_track_apple_music(self):
        self.execture_osascript(command='tell application "Music" to previous track')

    # Spotify
    def toggle_spotify(self):
        self.execture_osascript(
            command="""
        tell application "Spotify"
            if player state is playing then
                pause
            else
                play
            end if
        end tell
        """
        )

    def next_track_spotify(self):
        self.execture_osascript(command='tell application "Spotify" to next track')

    def previous_track_spotify(self):
        self.execture_osascript(command='tell application "Spotify" to previous track')

    # Brightness
    def increase_brightness(self):
        self.execture_osascript(command='tell application "System Events" to key code 144')

    def decrease_brightness(self):
        self.execture_osascript(command='tell application "System Events" to key code 145')

    # Sidebar (calendar, battery lvl etc.)
    def toggle_bar(self):
        self.execture_osascript(
            command="""
        tell application "System Events"
            tell process "ControlCenter"
                click menu bar item 1 of menu bar 1
            end tell
        end tell
        """
        )

    def open_calculator(self):
        self.open_app("Calculator")

    def open_terminal(self):
        self.open_app("Terminal")

    def open_google_chrome(self):
        self.open_app("Google Chrome")

    def open_spotify(self):
        self.open_app("Spotify")

    def open_finder(self):
        self.open_app("Finder")
