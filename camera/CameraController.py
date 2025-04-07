import gphoto2 as gp
import time


CAMERA_STARTUP_CONFIG = { "capturetarget": 0, "imageformat": 9 }
CAMERA_DEFAULT_CONFIG = { "aspectratio": 0, "picturestyle": 1, "aperture": 0, "shutterspeed": 37 }
MODES = [ CAMERA_DEFAULT_CONFIG, { "aspectratio": 0 }, { "aspectratio": 3 } ]

class CameraController:

    mode = 0
    camera = None
    config = CAMERA_STARTUP_CONFIG


    def __init__(self, logging):
        self.mode = 0
        self.config = CAMERA_DEFAULT_CONFIG
        self.logging = logging


    def connect(self):
        self.logging.info("{}: [CamCon] <connect> Connecting to camera".format(time.time()))

        self.camera = gp.check_result(gp.gp_camera_new())
        gp.check_result(gp.gp_camera_init(self.camera))

        self.logging.info("{}: [CamCon] <connect> Connected successfully to {}".format(time.time(), self.camera))

        self.camera_config = gp.check_result(gp.gp_camera_get_config(self.camera))
        self.reset_config()


    def disconnect(self):
        self.logging.info("{}: [CamCon] <disconnect> Disconnecting camera".format(time.time()))
        if self.camera:
            self.camera.exit()
            self.camera = None
        else:
            self.logging.debug("{}: [CamCon] <disconnect> No camera was connected".format(time.time()))


    def reconnect(self):
        self.logging.info("{}: [CamCon] <reconnect> Reconnecting camera".format(time.time()))
        self.disconnect()
        self.connect()


    def fallback(self):
        self.logging.debug("{}: [CamCon] <fallback> Going into Fallback!".format(time.time()))
        self.disconnect()
        while not self.camera:
            try:
                self.reconnect()
            except Exception as e:
                self.logging.debug("{}: [CamCon] <fallback> Connecting to Camera failed: {}".format(time.time(), str(e)))
                time.sleep(5)


    """
        Releases the shutter of the camera and returns the filepath of the picture taken.
        This method is unsafe. If something prevents the camera from shooting, an uncaught error is thrown.
    """
    def shoot(self):
        file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE)

        # Wait for camera to finish capture
        while True:
            event_type, event_data = self.camera.wait_for_event(5000)
            if event_type == gp.GP_EVENT_FILE_ADDED:
                break

        return file_path
        

    def set_mode(self, index):
        self.mode = index
        self.set_config(MODES[self.mode])


    def rotate_mode(self, forward):
        next_mode = 0
        if forward:
            next_mode = (self.mode + 1) % len(MODES)
        else:
            next_mode = self.mode - 1
            if next_mode < 0:
                next_mode = len(MODES) - 1
        
        self.set_mode(next_mode)
        


    """
        Sets the configuration of the camera.
        This method is unsafe. If uploading the config to the camera failes, an uncaught error is thrown.
    """
    def set_config(self, configurations):
        self.config = { **CAMERA_DEFAULT_CONFIG, **configurations }

        self.logging.info("{}: [CamCon] <set_config> Setting config to {}".format(time.time(), configurations))

        gp.check_result(gp.gp_camera_set_config(self.camera, self.camera_config))
        

    def reset_config(self):
        self.logging.info("{}: [CamCon] <reset_config> Resetting config".format(time.time()))

        self.set_config({ **CAMERA_DEFAULT_CONFIG, **CAMERA_STARTUP_CONFIG })
        self.mode = 0


    def get_file(self, path):
        self.logging.info("{}: [CamCon] <get_file> Getting file at '{}{}'".format(time.time(), path.folder, path.name))

        return self.camera.file_get(path.folder, path.name, gp.GP_FILE_TYPE_NORMAL)


# --- DEBUG METHODS ---

    def debug_set_config_property(self, config_name, value, leave_camera_dirty=False):
        if self.camera_config == None:
            self.logging.error("{}: [CamCon] <debug_set_config_property> Failed to set config, because no camera_config is loaded. Please make sure the camera is connected and initialized".format(time.time()))
            return

        setting = gp.check_result(gp.gp_widget_get_child_by_name(self.camera_config, config_name))

        if value < 0:
            self.logging.error("{}: [CamCon] <debug_set_config_property> Failed to set config. Value must not be less than 0".format(time.time()))
            return
        options_count = gp.check_result(gp.gp_widget_count_choices(setting))
        if value >= options_count:
            self.logging.error("{}: [CamCon] <debug_set_config_property> Failed to set config. Value is out of range. Max option is {}".format(time.time(), str(value - 1)))
            return

        choice = gp.check_result(gp.gp_widget_get_choice(setting, value))
        self.logging.info("You chose as " + config_name + ": " + str(choice))
        gp.check_result(gp.gp_widget_set_value(setting, choice))

        if not leave_camera_dirty:
            self.update_camera_config()
