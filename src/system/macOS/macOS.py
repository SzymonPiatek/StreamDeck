from src.system.system.system import System


class MacOS(System):
    def __init__(self):
        super().__init__(name="MacOS")

    def event_listener(self):
        print("Event")
