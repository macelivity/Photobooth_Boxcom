import os
import time
from datetime import datetime
import threading
import logging


IMAGE_TARGET_DIRECTORY = "/home/photobooth/boxcom/images"
RAW_IMAGE_TARGET_DIRECTORY = "/home/photobooth/boxcom/images_raw"
FILENAME_DIGIT_COUNT = 6
SECONDS_TO_GO_IDLE = 90.0


logging.basicConfig(filename="backend.log", level=logging.DEBUG)


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
	print("startup() \t- Starts all processes for input and camera control")
	print("shutdown() \t- Ends all processes for input and camera control")





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



def consume_remote_control_event(event):
	try:
		take_picture()
		time.sleep(4)
	except Exception as e:
		print("Exception caught while consuming remote control event")
		print(e)
		shutdown()
		time.sleep(1)
		initialize_camera()

def is_valid_trigger(event, last_photo_time):
	if event.type != evdev.ecodes.EV_KEY: return False
	if event.sec < last_photo_time + 4: return False
	if event.value != 1: return False
	return True


def listen_for_remote_control():
	global remote_control
	last_photo_time = time.time()
	for event in remote_control.read_loop():
		if not is_valid_trigger(event, last_photo_time):
			continue
		consume_remote_control_event(event)
		last_photo_time = time.time()
		print("Photo taken.")
	
	
def obsolete_listen_for_remote_control():
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
	global camera
	camera.exit()


if __name__ == "__main__":
	startup()


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