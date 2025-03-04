from RemoteInput import RemoteInput
import threading
import logging
import gphoto2 as gp


logging.basicConfig(filename="enterprise.log", level=logging.DEBUG)


global camera
camera = gp.check_result(gp.gp_camera_new())
gp.check_result(gp.gp_camera_init(camera))

def print_events():
    while True:
        event_type, event_data = camera.wait_for_event(5000)
        print("Event captured: " + str(event_type) + "; <> " + str(event_data))




print("############################################################")

def shoot():
    global camera
    camera.capture(gp.GP_CAPTURE_IMAGE)

rem = RemoteInput(logging)
rem.connect()
rem.set_action("*", shoot)

event_printer = threading.Thread(target=print_events())
event_printer.start()