class Device:
    def __init__(self, name, device_type, device_id=None):
        self.id = device_id
        self.name = name
        self.type = device_type

    def __repr__(self):
        return f"Device(name={self.name}, device_id={self.id}, device_type={self.type})"
