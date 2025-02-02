class Device:
    def __init__(self, device_id, name, device_type):
        self.id = device_id
        self.name = name
        self.type = device_type

    def __repr__(self):
        return f"Device(name={self.name}, device_id={self.id}, device_type={self.type})"
