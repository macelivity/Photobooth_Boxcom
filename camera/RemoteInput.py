import evdev


REMOTE_CONTROL_NAME = "Logitech USB Receiver"

class RemoteInput:

    controller = None
    actions = {}


    def __init(self):
        self.controller = None
        self.actions = {}

    
    def connect():
        self.controller = None
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if device.name == REMOTE_CONTROL_NAME:
                self.controller = device
                break
        raise Exception("No controller with title '" + REMOTE_CONTROL_NAME + "' was found.")


    def start_listen():
        last_photo_time = time.time()
        for event in remote_control.read_loop():
            get_action(event.code)()


    def get_action(key):
        return self.actions[key]

    def set_action(key, action):
        self.actions[key] = action