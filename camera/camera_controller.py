import os
import time
from datetime import datetime
import threading
import logging
from CameraController import CameraController
from RemoteInput import RemoteInput


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



def normalize_id(id):
	 return "0" * (FILENAME_DIGIT_COUNT - len(id)) + id

def save_image(path):
	try:
		global image_index
		logging.info("Loading jpg from {}/{}...".format(path.folder, path.name))
		file = cam.get_file(path)
		id = normalize_id(str(image_index))
		file.save("{}/img{}.jpg".format(IMAGE_TARGET_DIRECTORY, id))
		logging.info("Successfully saved jpg at {}/img{}.jpg!".format(IMAGE_TARGET_DIRECTORY, id))
		image_index += 1

	except Exception as e:
		logging.error("Something went wrong while trying to save a JPG picture. Exception message: " + str(e))



def take_picture():
	global cam
	
	if cam == None:
		logging.info("Can't take picture because no camera is connected")
		return

	filepath = cam.shoot()
	save_image(filepath)


def start_listen_for_remote_control():
	global remote_control_listener
	remote_control_listener = threading.Thread(target=rem.start_listen())
	remote_control_listener.start()


def stop_listen_for_remote_control():
	global remote_control_listener
	if not "remote_control_listener" in globals():
		return
	remote_control_listener.listen = False


def startup():
	global cam
	cam = CameraController()
	cam.connect()

	global rem
	rem = RemoteInput()
	rem.connect()
	rem.set_action("*", take_picture)
	rem.start_listen()


def shutdown():
	stop_listen_for_remote_control()
	global cam
	cam.disconnect()


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