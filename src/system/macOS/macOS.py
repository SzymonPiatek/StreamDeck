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
                return parts[1].strip().replace('"', "")  # Usunięcie cudzysłowów

        return None
