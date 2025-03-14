import evdev
import time


REMOTE_CONTROL_NAME = "Logitech USB Receiver"
EVENT_COOLDOWN = 1

class RemoteInput:

    controller = None
    actions = {}
    last_event_time = None


    def __init__(self, logging):
        self.controller = None
        self.actions = {}
        self.last_event_time = time.time()
        self.logging = logging

    
    def connect(self):
        self.controller = None
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if device.name == REMOTE_CONTROL_NAME:
                self.controller = device
                return
        raise Exception("No controller with title '" + REMOTE_CONTROL_NAME + "' was found.")


    def consume_action(self, action):
        try:
            action()
        except Exception as e:
            self.logging.error(e)


    def start_listen(self):
        last_photo_time = time.time()
        for event in self.controller.read_loop():
            if self.is_valid_event(event):
                print("Input Event caught: " + str(event))
                if self.has_action(event.code):
                    self.consume_action(self.get_action(event.code))
                    self.last_event_time = time.time()
                if self.has_action("*"):
                    self.consume_action(self.get_action("*"))
                    self.last_event_time = time.time()


    def has_action(self, key):
        return key in self.actions

    def get_action(self, key):
        return self.actions[key]

    def set_action(self, key, action):
        self.actions[key] = action


    def is_valid_event(self, event):
        if event.type != evdev.ecodes.EV_KEY: return False
        if event.sec < self.last_event_time + EVENT_COOLDOWN: return False
        if event.value != 1: return False
        return True