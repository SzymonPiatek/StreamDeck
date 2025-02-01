import subprocess

from src.system.system.system import System


class MacOS(System):
    def __init__(self):
        super().__init__(name="MacOS")

    def recognize_devices(self):
        devices = [self.get_builtin_keyboard()]

        usb_devices = self.get_usb_devices()
        bluetooth_devices = self.get_bluetooth_devices()

        for usb in usb_devices:
            devices.append(usb)
        for bluetooth in bluetooth_devices:
            devices.append(bluetooth)

        return devices

    def get_usb_devices(self):
        result = subprocess.getoutput("system_profiler SPUSBDataType")
        devices = [line.strip() for line in result.split("\n") if "Product Name:" in line]

        return devices

    def get_bluetooth_devices(self):
        result = subprocess.getoutput("system_profiler SPBluetoothDataType")
        devices = []

        prev_line = None
        for line in result.split("\n"):
            if "Connected: Yes" in line:
                devices.append(prev_line.strip())
            prev_line = line

        return devices if devices else []

    def get_builtin_keyboard(self):
        result = subprocess.getoutput("ioreg -r -c AppleEmbeddedKeyboard -d 1 | grep -i 'Product'")

        if result:
            parts = result.split("=")
            if len(parts) > 1:
                name = parts[1].split("\n")
                return name[0].replace('"', "")

        return None

    def volume_down(self):
        try:
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    "set volume output volume (output volume of (get volume settings) - 10) --100 max",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"DEBUG: Błąd zmniejszania głośności: {e}")

    def volume_up(self):
        try:
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    "set volume output volume (output volume of (get volume settings) + 10) --100 max",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"DEBUG: Błąd zwiększania głośności: {e}")

    def mute_unmute(self):
        try:
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
        except subprocess.CalledProcessError as e:
            print(f"DEBUG: Błąd wyciszania: {e}")
