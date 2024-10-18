import os
import time
from datetime import datetime
import threading
import evdev
import gphoto2 as gp
import logging


IMAGE_TARGET_DIRECTORY = "/home/photobooth/photobooth/images"
RAW_IMAGE_TARGET_DIRECTORY = "/home/photobooth/photobooth/images_raw"
FILENAME_DIGIT_COUNT = 6
REMOTE_CONTROL_NAME = "Logitech USB Receiver"
CAMERA_STARTUP_CONFIG = { "capturetarget": 0, "imageformat": 9,  }
CAMERA_DEFAULT_CONFIG = { "aspectratio": 1, "picturestyle": 1, "aperture": 0, "shutterspeed": 32 }
MODES = [ CAMERA_DEFAULT_CONFIG, { "aspectratio": 0 }, { "aspectratio": 3 } ]
SECONDS_TO_GO_IDLE = 90.0


logging.basicConfig(filename="backend.log", level=logging.DEBUG)


global current_mode
current_mode = 0
global change_mode_timestamp
change_mode_timestamp = datetime.now()

# calculate start image_index
global image_index
image_index = 0
if len(os.listdir(IMAGE_TARGET_DIRECTORY)) > 0:
	image_index = max([int(f[3:-4]) for f in os.listdir(IMAGE_TARGET_DIRECTORY)]) + 1
logging.info("Start image index: " + str(image_index))


def help():
	print("initialize_camera() \t- Initializes connection to the camera retrieves camera_config")
	print("register_remote_control() \t- Sets remote_control to the connected remote control InputDevice")
	print("take_picture() \t- Takes a picture and ...")
	print("print_config_categories() \t- Outputs a help message containing all config categories of the connected camera")
	print("print_config_options(int: category_index) \t- Outputs a help message containing all config options of the category with the specified index (as shown in print_config_categories())")
	print("set_config(str: config_name, int: value) \t- Sets the config option with the name config_name to the desired value and updates it on the camera")
	print("change_to_next_mode() \t- Changes the camera settings to the next mode as defined in MODES")
	print("change_to_previous_mode() \t- Changes the camera settings to the previous mode as defined in MODES")
	print("reset_camera_config() \t- Resets all camera configs to the values specified in CAMERA_DEFAULT_CONFIG. If the value of a setting is not specified therein, it stays the same")
	print("start_listen_for_remote_control() \t- ")
	print("stop_listen_for_remote_control() \t- ")


def reset_camera():
	apply_configurations({ **CAMERA_DEFAULT_CONFIG, **CAMERA_STARTUP_CONFIG })
	global current_mode
	current_mode = 0


def initialize_camera():
	global camera
	camera = gp.check_result(gp.gp_camera_new())
	gp.check_result(gp.gp_camera_init(camera))
	global camera_config
	camera_config = gp.check_result(gp.gp_camera_get_config(camera))

	reset_camera()


def register_remote_control():
	global remote_control
	remote_control = None
	devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
	for device in devices:
		if device.name == REMOTE_CONTROL_NAME:
			remote_control = device
			break


def normalize_id(id):
    return "0" * (FILENAME_DIGIT_COUNT - len(id)) + id

def save_image(folder, name):
	try:
		global image_index
		logging.info("Loading jpg from {}/{}...".format(folder, name))
		file = camera.file_get(folder, name, gp.GP_FILE_TYPE_NORMAL)
		id = normalize_id(str(image_index))
		file.save("{}/img{}.jpg".format(IMAGE_TARGET_DIRECTORY, id))
		logging.info("Successfully saved jpg at {}/img{}.jpg!".format(IMAGE_TARGET_DIRECTORY, id))
		image_index += 1

	except Exception as e:
		logging.error("Something went wrong while trying to save a JPG picture. Exception message: " + str(e))




def take_picture():
	global camera
	file_path = camera.capture(gp.GP_CAPTURE_IMAGE)

	# Wait for camera to finish capture
	while True:
		event_type, event_data = camera.wait_for_event(8000)
		if event_type == gp.GP_EVENT_FILE_ADDED:
			break

	save_image(file_path.folder, file_path.name)


def print_config_categories():
	global camera_config
	if camera_config == None:
		print("camera_config does not exist. Please initialize the camera.")
		return

	category_count = camera_config.count_children()
	for n in range(category_count):
		category = camera_config.get_child(n)
		label = "{}: {} ({})".format(n, category.get_label(), category.get_name())
		print(label)

def print_config_options(category_index):
	global camera_config
	if camera_config == None:
		print("camera_config does not exist. Please initialize the camera.")
		return

	category = camera_config.get_child(category_index)
	options_count = category.count_children()
	for n in range(options_count):
		option = category.get_child(n)
		label = "{} ({}): ({})".format(option.get_label(), option.get_name(), option.get_value())
		print(label)



def update_camera_config():
	global camera
	global camera_config
	for i in range(5):
		try:
			gp.check_result(gp.gp_camera_set_config(camera, camera_config))
			logging.info("\tCamera config was updated successfully.")
			return
		except Exception as e:
			logging.error("An error occured while updating config on the camera. Message: " + str(e))
			time.sleep(0.5)
	logging.error("Failed to update camera config.")


def set_config(config_name, value, leave_camera_dirty=False):
	global camera
	global camera_config
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


def apply_configurations(configurations):
	config = { **CAMERA_DEFAULT_CONFIG, **configurations }
	for config_name in config.keys():
		set_config(config_name, config[config_name], True)

	update_camera_config()


def reset_camera_config():
	apply_configurations(CAMERA_DEFAULT_CONFIG)


def change_to_default_mode():
	global current_mode
	current_mode = 0
	apply_configurations(MODES[current_mode])



def change_to_default_mode_if_idle():
	global change_mode_timestamp
	deltatime = datetime.now() - change_mode_timestamp
	if deltatime.total_seconds() >= SECONDS_TO_GO_IDLE:
		change_to_default_mode()


def change_to_next_mode():
	global current_mode
	current_mode += 1
	global change_mode_timestamp
	change_mode_timestamp = datetime.now()
	if current_mode >= len(MODES):
		current_mode = 0
	apply_configurations(MODES[current_mode])
	timer = threading.Timer(SECONDS_TO_GO_IDLE, change_to_default_mode_if_idle)
	timer.start()


def change_to_previous_mode():
	global current_mode
	current_mode -= 1
	global change_mode_timestamp
	change_mode_timestamp = datetime.now()
	if current_mode < 0:
		current_mode = len(MODES) - 1
	apply_configurations(MODES[current_mode])
	timer = threading.Timer(SECONDS_TO_GO_IDLE, change_to_default_mode_if_idle)
	timer.start()



def consume_remote_control_event(event):
	take_picture()


def listen_for_remote_control():
	global remote_control
	thread = threading.currentThread()
	while getattr(thread, "listen", True):
		try:
			event = remote_control.read_one()
			if event == None:
				continue
		except:
			logging.error("Caught an exception while reading control event. Exception message: " + str(e))

		try:
			consume_remote_control_event(event)
		except Exception as e:
			logging.error("Caught an exception while consuming a remote control event. Exception message: " + str(e))

		try:
			events_cleared = False
			while not events_cleared:
				events_cleared = remote_control.read_one() == None
		except Exception as e:
			logging.error("Caught an exception while clearing all remote control events. Exception message: " + str(e))


def start_listen_for_remote_control():
	global remote_control_listener
	remote_control_listener = threading.Thread(target=listen_for_remote_control)
	remote_control_listener.start()


def stop_listen_for_remote_control():
	global remote_control_listener
	if not "remote_control_listener" in globals():
		return
	remote_control_listener.listen = False


def startup():
	try:
		register_remote_control()
		initialize_camera()
		start_listen_for_remote_control()
	except:
		logging.error("Automatic startup failed")
		print("Automatic startup failed. Please repeat manually")


def shutdown():
	stop_listen_for_remote_control()
	camera.exit()


#print(str(event.value) + "; c: " + str(event.code))
#print("Received an event: " + str(event.code) + " = " + str(event.value) + "\n")
#if event.value == 458827 or event.code == 104:
#	change_to_previous_mode()
#	time.sleep(0.5)
#elif event.value == 458830 or event.code == 109:
#	change_to_next_mode()
#	time.sleep(0.5)
#elif event.value == 458814 or event.value == 458897:
#	take_picture()
#elif event.value == 458807 or event.code == 52:
#	take_picture()