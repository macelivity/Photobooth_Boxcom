import evdev
import time


REMOTE_CONTROL_NAME = "Logitech USB Receiver"
EVENT_COOLDOWN = 0
LISTEN = True

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
        self.logging.info("{}: [RemInp] <connect> Connecting to remote controller".format(time.time()))
        self.controller = None
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if device.name == REMOTE_CONTROL_NAME:
                self.controller = device
                return
        raise Exception("No controller with title '" + REMOTE_CONTROL_NAME + "' was found.")
    

    def disconnect(self):
        LISTEN = False
        self.controller = None
    

    def fallback(self):
        self.disconnect()
        while not self.controller:
            try:
                self.connect()
            except Exception as e:
                self.logging.debug("{}: [RemInp] <fallback> Connecting to Remote Input failed: {}".format(time.time(), str(e)))
                time.sleep(5)


    def consume_action(self, action):
        try:
            action()
        except Exception as e:
            self.logging.error(e)


    def start_listen(self):
        LISTEN = True
        self.logging.info("{}: [RemInp] <start_listen> Start listening for remote control events".format(time.time()))
        for event in self.controller.read_loop():
            if not LISTEN:
                return
            if self.is_valid_event(event):
                self.logging.info("{}: [RemInp] <start_listen> Input Event caught: {}".format(time.time(), str(event)))
                if self.has_action(event.code):
                    self.consume_action(self.get_action(event.code))
                    self.last_event_time = time.time()
                if self.has_action("*"):
                    self.consume_action(self.get_action("*"))
                    self.last_event_time = time.time()


    def stop_listen(self):
        self.logging.info("{}: [RemInp] <stop_listen> Stop listening for remote control".format(time.time()))
        LISTEN = False


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