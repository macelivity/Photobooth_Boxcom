import gphoto2 as gp


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
        self.camera = gp.check_result(gp.gp_camera_new())
        gp.check_result(gp.gp_camera_init(self.camera))
        self.camera_config = gp.check_result(gp.gp_camera_get_config(self.camera))


    def disconnect(self):
        self.camera.exit()


    """
        Releases the shutter of the camera and returns the filepath of the picture taken.
        This method is unsafe. If something prevents the camera from shooting, an uncaught error is thrown.
    """
    def shoot(self):
        file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE)

        # Wait for camera to finish capture
        while True:
            event_type, event_data = self.cam.wait_for_event(5000)
            if event_type == gp.GP_EVENT_FILE_ADDED:
                break

        return file_path
        

    def set_mode(self, index):
        self.mode = index
        set_config(MODES[self.mode])


    def rotate_mode(self, forward):
        next_mode = 0
        if forward:
            next_mode = (self.mode + 1) % len(MODES)
        else:
            next_mode = self.mode - 1
            if next_mode < 0:
                next_mode = len(MODES) - 1
        
        set_mode(next_mode)
        


    """
        Sets the configuration of the camera.
        This method is unsafe. If uploading the config to the camera failes, an uncaught error is thrown.
    """
    def set_config(self, configurations):
        self.config = { **CAMERA_DEFAULT_CONFIG, **configurations }

        gp.check_result(gp.gp_camera_set_config(self.camera, self.camera_config))
        

    def reset_config(self):
        self.set_config({ **CAMERA_DEFAULT_CONFIG, **CAMERA_STARTUP_CONFIG })
        self.mode = 0


    def get_file(self, path):
        camera.file_get(path.folder, path.name, gp.GP_FILE_TYPE_NORMAL)


# --- DEBUG METHODS ---

    def debug_set_config_property(self, config_name, value, leave_camera_dirty=False):
        if camera_config == None:
            logging.error("Failed to set config, because no camera_config is loaded. Please make sure the camera is connected and initialized")
            return

        setting = gp.check_result(gp.gp_widget_get_child_by_name(camera_config, config_name))

        if value < 0:
            logging.error("Failed to set config. Value must not be less than 0")
            return
        options_count = gp.check_result(gp.gp_widget_count_choices(setting))
        if value >= options_count:
            logging.error("Failed to set config. Value is out of range. Max option is " + str(value - 1))
            return

        choice = gp.check_result(gp.gp_widget_get_choice(setting, value))
        logging.info("You chose as " + config_name + ": " + str(choice))
        gp.check_result(gp.gp_widget_set_value(setting, choice))

        if not leave_camera_dirty:
            update_camera_config()
