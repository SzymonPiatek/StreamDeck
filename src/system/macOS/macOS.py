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
            {"name": "Volume +", "function": self.volume_up},
            {"name": "Volume -", "function": self.volume_down},
            {"name": "Mute/Unmute", "function": self.mute_unmute},
            {"name": "Brightness +", "function": self.increase_brightness},
            {"name": "Brightness -", "function": self.decrease_brightness},
            {"name": "Toogle disturb", "function": self.toggle_do_not_disturb},
            {"name": "Open app", "function": self.open_app},
            {"name": "Open url", "function": self.open_url},
            {"name": "Toggle music", "function": self.toggle_music},
            {"name": "Next track", "function": self.next_track},
            {"name": "Previous track", "function": self.previous_track},
            {"name": "Toggle Spotify", "function": self.toggle_spotify},
            {"name": "Next track spotify", "function": self.next_spotify},
            {"name": "Previous track spotify", "function": self.previous_spotify},
        ]

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

        current_device = None
        prev_line = None

        for line in result.split("\n"):
            line = line.strip()

            if "Connected: Yes" in line and prev_line:
                device_name = prev_line.strip()
                current_device = Device(name=device_name, device_type="Bluetooth")

            if current_device:
                devices.append(current_device)
                current_device = None

            prev_line = line

        return devices

    def get_builtin_keyboard(self):
        result = subprocess.getoutput("ioreg -r -c AppleEmbeddedKeyboard -d 1 | grep -i 'Product'")

        if result:
            device_name = None
            device_id = None
            device_type = "Builtin"

            for line in result.split("\n"):
                line = line.strip()

                if line.startswith('"Product"'):
                    match = re.search(r'"Product" = "(.*?)"', line)
                    if match:
                        device_name = match.group(1)

                elif line.startswith('"ProductID"'):
                    match = re.search(r'"ProductID" = (\d+)', line)
                    if match:
                        device_id = int(match.group(1))

                builtin_device = Device(name=device_name, device_id=device_id, device_type=device_type)

                return builtin_device
        return None

    # Audio
    @handle_subprocess_error
    def volume_up(self):
        subprocess.run(
            ["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10) --100 max"],
            check=True,
        )

    @handle_subprocess_error
    def volume_down(self):
        subprocess.run(
            ["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10) --100 max"],
            check=True,
        )

    @handle_subprocess_error
    def mute_unmute(self):
        subprocess.run(
            [
                "osascript",
                "-e",
                """
            set currentMute to output muted of (get volume settings)
            if currentMute then
                set volume output muted false
            else
                set volume output muted true
            end if
        """,
            ],
            check=True,
        )

    # Brightness
    @handle_subprocess_error
    def increase_brightness(self):
        subprocess.run(["osascript", "-e", 'tell application "System Events" to key code 144'], check=True)

    @handle_subprocess_error
    def decrease_brightness(self):
        subprocess.run(["osascript", "-e", 'tell application "System Events" to key code 145'], check=True)

    # Do not disturb
    @handle_subprocess_error
    def toggle_do_not_disturb(self):
        script = """
        tell application "System Events"
            tell process "ControlCenter"
                click menu bar item 1 of menu bar 1
            end tell
        end tell
        """
        subprocess.run(["osascript", "-e", script], check=True)

    # Apps
    @handle_subprocess_error
    def open_app(self, app_name):
        subprocess.run(["open", "-a", app_name], check=True)

    # Urls
    @handle_subprocess_error
    def open_url(self, url):
        subprocess.run(["open", url], check=True)

    # Apple Music
    @handle_subprocess_error
    def toggle_music(self):
        script = """
        tell application "Music"
            if player state is playing then
                pause
            else
                play
            end if
        end tell
        """
        subprocess.run(["osascript", "-e", script], check=True)

    @handle_subprocess_error
    def next_track(self):
        subprocess.run(["osascript", "-e", 'tell application "Music" to next track'], check=True)

    @handle_subprocess_error
    def previous_track(self):
        subprocess.run(["osascript", "-e", 'tell application "Music" to previous track'], check=True)

    # Spotify
    @handle_subprocess_error
    def toggle_spotify(self):
        script = """
        tell application "Spotify"
            if player state is playing then
                pause
            else
                play
            end if
        end tell
        """
        subprocess.run(["osascript", "-e", script], check=True)

    @handle_subprocess_error
    def next_spotify(self):
        subprocess.run(["osascript", "-e", 'tell application "Spotify" to next track'], check=True)

    @handle_subprocess_error
    def previous_spotify(self):
        subprocess.run(["osascript", "-e", 'tell application "Spotify" to previous track'], check=True)

    def device_listener(self):
        try:
            keyboard.on_press(self.application.on_key_press)
            keyboard.wait()
        except Exception as e:
            print(f"DEBUG: Błąd podczas nasłuchiwania klawiszy: {e}")
