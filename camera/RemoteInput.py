import evdev
import time


REMOTE_CONTROL_NAME = "Logitech USB Receiver"
EVENT_COOLDOWN = 4

class RemoteInput:

    controller = None
    actions = {}
    last_event_time = None


    def __init(self):
        self.controller = None
        self.actions = {}
        self.last_event_time = None

    
    def connect(self):
        self.controller = None
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if device.name == REMOTE_CONTROL_NAME:
                self.controller = device
                return
        raise Exception("No controller with title '" + REMOTE_CONTROL_NAME + "' was found.")


    def start_listen(self):
        last_photo_time = time.time()
        for event in self.controller.read_loop():
            if is_valid_event(event):
                get_action(event.code)()
                get_action("*")()


    def get_action(self, key):
        return self.actions[key]

    def set_action(self, key, action):
        self.actions[key] = action


    def is_valid_event(self, event):
        if event.type != evdev.ecodes.EV_KEY: return False
        if event.sec < self.last_event_time + EVENT_COOLDOWN: return False
        if event.value != 1: return False
        return True