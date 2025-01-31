from src.system.system.system import System


class Windows(System):
    def __init__(self):
        super().__init__(name="Windows")

    def event_listener(self):
        print("Event")
